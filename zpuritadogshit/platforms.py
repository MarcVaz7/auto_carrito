from abc import ABC, abstractmethod
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import urllib.parse
import getpass
from config_manager import ConfigManager

class PlatformBase(ABC):
    def __init__(self, driver, utils):
        self.driver = driver
        self.utils = utils
        self.config_manager = ConfigManager()
    
    @abstractmethod
    def login(self):
        pass
    
    @abstractmethod
    def buscar_carta(self, nombre_carta):
        pass
    
    @abstractmethod
    def seleccionar_carta_mas_barata(self, nombre_carta):
        pass
    
    @abstractmethod
    def buscar_vendedores(self, condiciones, cantidad_necesaria=1):
        pass

class CardTraderPlatform(PlatformBase):
    def login(self):
        """Inicia sesión en CardTrader"""
        print("🔐 Iniciando sesión en CardTrader...")
        
        # Verificar si ya estamos logueados
        if self._ya_esta_logueado():
            print("✅ Ya hay una sesión activa en CardTrader")
            return True
        
        # Obtener credenciales
        creds = self.config_manager.get_credentials('cardtrader')
        if not creds.get('username') or not creds.get('password'):
            print("❌ No se encontraron credenciales para CardTrader")
            return self._pedir_credenciales_interactivo('cardtrader')
        
        try:
            # Ir a la página de login
            self.driver.get("https://www.cardtrader.com/es/users/sign_in")
            time.sleep(3)
            
            # Rellenar formulario de login
            username_field = self.driver.find_element(By.ID, "user_email")
            password_field = self.driver.find_element(By.ID, "user_password")
            
            username_field.clear()
            username_field.send_keys(creds['username'])
            
            password_field.clear()
            password_field.send_keys(creds['password'])
            
            # Enviar formulario
            login_button = self.driver.find_element(By.NAME, "commit")
            login_button.click()
            time.sleep(3)
            
            # Verificar si el login fue exitoso
            if self._ya_esta_logueado():
                print("✅ Login exitoso en CardTrader")
                return True
            else:
                print("❌ Error en el login de CardTrader")
                return False
                
        except Exception as e:
            print(f"❌ Error durante el login en CardTrader: {e}")
            return False
    
    def _ya_esta_logueado(self):
        """Verifica si ya hay una sesión activa"""
        try:
            # Buscar elementos que indican que el usuario está logueado
            elementos_logueado = [
                "//a[contains(@href, '/users/sign_out')]",
                "//a[contains(text(), 'Mi cuenta')]",
                "//a[contains(text(), 'My account')]"
            ]
            
            for elemento in elementos_logueado:
                try:
                    if self.driver.find_elements(By.XPATH, elemento):
                        return True
                except:
                    continue
            return False
        except:
            return False
    
    def _pedir_credenciales_interactivo(self, platform):
        """Pide credenciales al usuario de forma interactiva"""
        print(f"\n🔐 Credenciales necesarias para {platform.upper()}")
        print("Por favor, ingresa tus datos de acceso:")
        
        username = input("Usuario/Email: ").strip()
        password = getpass.getpass("Contraseña: ").strip()
        
        if not username or not password:
            print("❌ Se requieren tanto usuario como contraseña")
            return False
        
        # Guardar credenciales
        if self.config_manager.set_credentials(platform, username, password):
            print("✅ Credenciales guardadas")
            # Intentar login nuevamente
            return self.login()
        else:
            print("❌ Error guardando credenciales")
            return False

    def buscar_carta(self, nombre_carta):
        """Busca la carta desde la página principal usando el buscador ManaSearch"""
        print(f"🔍 CardTrader: Iniciando búsqueda desde página principal...")
        
        # Ir a la página principal de Magic
        url_principal = "https://www.cardtrader.com/es/magic"
        self.driver.get(url_principal)
        time.sleep(5)
        self.utils.cerrar_popups()
        
        print("✓ Página principal cargada")
        
        # Buscar el campo de búsqueda ManaSearch
        try:
            buscador = self.driver.find_element(By.ID, "manasearch-input")
            print("✅ Buscador ManaSearch encontrado")
            
            # Limpiar y escribir el nombre de la carta
            buscador.clear()
            buscador.send_keys(nombre_carta)
            time.sleep(1)
            
            # Enviar la búsqueda con ENTER
            print("⌨️ Enviando búsqueda con ENTER...")
            buscador.send_keys(Keys.RETURN)
            time.sleep(5)
            
            print("✓ Búsqueda enviada, esperando resultados...")
            return True
            
        except Exception as e:
            print(f"❌ No se pudo encontrar o usar el buscador: {e}")
            return False
    
    def seleccionar_carta_mas_barata(self, nombre_carta):
        """Usa el CardSelector existente para CardTrader"""
        from card_selector import CardSelector
        selector = CardSelector(self.driver, self.utils)
        return selector.seleccionar_carta_mas_barata(nombre_carta)
    
    def buscar_vendedores(self, condiciones, cantidad_necesaria=1):
        """Usa el SellerFinder existente para CardTrader"""
        from seller_finder import SellerFinder
        finder = SellerFinder(self.driver, self.utils)
        return finder.buscar_vendedores_con_zero_real(condiciones, cantidad_necesaria)

class CardMarketPlatform(PlatformBase):
    def login(self):
        """Inicia sesión en CardMarket - MEJORADO"""
        print("🔐 Iniciando sesión en CardMarket...")
        
        # Verificar si ya estamos logueados
        if self._ya_esta_logueado():
            print("✅ Ya hay una sesión activa en CardMarket")
            return True
        
        # Obtener credenciales
        creds = self.config_manager.get_credentials('cardmarket')
        if not creds.get('username') or not creds.get('password'):
            print("❌ No se encontraron credenciales para CardMarket")
            return self._pedir_credenciales_interactivo('cardmarket')
        
        try:
            # FORZAR navegación directa a la página de login
            print("🌐 Navegando directamente a la página de login...")
            self.driver.get("https://www.cardmarket.com/es/Magic/Login")
            time.sleep(3)
            
            # Verificar que estamos en la página correcta
            current_url = self.driver.current_url
            print(f"📄 URL actual: {current_url}")
            
            if "Login" not in current_url:
                print("⚠️ No estamos en la página de login, redirigiendo...")
                self.driver.get("https://www.cardmarket.com/es/Magic/Login")
                time.sleep(3)
            
            # Esperar a que cargue el formulario
            print("⏳ Esperando a que cargue el formulario de login...")
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            
            print("✅ Formulario de login cargado")
            
            # Rellenar formulario de login
            username_field = self.driver.find_element(By.NAME, "username")
            password_field = self.driver.find_element(By.NAME, "userPassword")
            
            # Limpiar campos primero
            username_field.clear()
            password_field.clear()
            
            # Ingresar credenciales
            username_field.send_keys(creds['username'])
            print("✅ Usuario ingresado")
            
            password_field.send_keys(creds['password'])
            print("✅ Contraseña ingresada")
            
            # Esperar un momento para que se habilite el botón
            time.sleep(2)
            
            # Buscar el botón de submit
            login_button = self.driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Iniciar sesión']")
            
            # Verificar si el botón está habilitado
            if login_button.get_attribute("disabled"):
                print("⚠️ Botón deshabilitado, intentando habilitarlo...")
                # Intentar hacer click en otros campos para activar validación
                username_field.click()
                time.sleep(1)
                password_field.click()
                time.sleep(1)
            
            # Hacer click en el botón usando JavaScript para evitar problemas
            print("🖱️ Haciendo click en el botón de login...")
            self.driver.execute_script("arguments[0].click();", login_button)
            
            # Esperar a que se procese el login
            print("⏳ Procesando login...")
            time.sleep(5)
            
            # Verificar redirección
            new_url = self.driver.current_url
            print(f"📄 Nueva URL: {new_url}")
            
            # Verificar si el login fue exitoso
            if self._ya_esta_logueado():
                print("✅ Login exitoso en CardMarket")
                return True
            else:
                # Verificar si hay mensajes de error
                if self._hay_error_login():
                    print("❌ Error en las credenciales de CardMarket")
                    # Limpiar credenciales incorrectas
                    self.config_manager.clear_credentials('cardmarket')
                    print("🔐 Credenciales incorrectas eliminadas")
                    return False
                else:
                    print("❌ Error desconocido en el login de CardMarket")
                    print("💡 Intentando verificar manualmente...")
                    
                    # Intentar navegar a una página que requiera login
                    self.driver.get("https://www.cardmarket.com/es/Magic/Users/Account")
                    time.sleep(3)
                    
                    if self._ya_esta_logueado():
                        print("✅ Login verificado manualmente - ¡éxito!")
                        return True
                    else:
                        return False
                
        except Exception as e:
            print(f"❌ Error durante el login en CardMarket: {e}")
            return False
    
    def _hay_error_login(self):
        """Verifica si hay mensajes de error en el login"""
        try:
            # Buscar mensajes de error comunes
            errores = [
                "//*[contains(text(), 'incorrecto')]",
                "//*[contains(text(), 'error')]",
                "//*[contains(text(), 'invalid')]",
                "//*[contains(text(), 'olvidado')]",
                "//*[contains(@class, 'error')]",
                "//*[contains(@class, 'alert-danger')]",
                "//*[contains(@class, 'text-danger')]"
            ]
            
            for error in errores:
                try:
                    elementos = self.driver.find_elements(By.XPATH, error)
                    for elemento in elementos:
                        if elemento.is_displayed():
                            print(f"⚠️ Mensaje de error encontrado: {elemento.text}")
                            return True
                except:
                    continue
            return False
        except:
            return False
    
    def _ya_esta_logueado(self):
        """Verifica si ya hay una sesión activa en CardMarket - MEJORADO"""
        try:
            # Verificar URL actual primero
            current_url = self.driver.current_url.lower()
            print(f"🔍 Verificando sesión en URL: {current_url}")
            
            # Si estamos en páginas que requieren login y no redirigen, estamos logueados
            if any(page in current_url for page in ['/account', '/messages', '/wants', '/shoppingcart']):
                return True
            
            # Si estamos en login page, probablemente no estamos logueados
            if any(page in current_url for page in ['/login', '/signin']):
                return False
            
            # Buscar elementos que indican que el usuario está logueado
            elementos_logueado = [
                "//a[contains(@href, 'Logout')]",
                "//a[contains(text(), 'Mi cuenta')]",
                "//a[contains(@href, 'Messages')]",
                "//a[contains(@href, 'Wants')]",
                "//span[contains(text(), 'Bienvenido')]",
                "//div[contains(@class, 'user-menu')]",
                "//div[contains(@class, 'user-info')]",
                "//a[contains(@class, 'account')]"
            ]
            
            for elemento in elementos_logueado:
                try:
                    if "//" in elemento:
                        elementos = self.driver.find_elements(By.XPATH, elemento)
                    else:
                        elementos = self.driver.find_elements(By.CSS_SELECTOR, elemento)
                    
                    for elem in elementos:
                        if elem.is_displayed():
                            print(f"✅ Elemento de sesión encontrado: {elemento}")
                            return True
                except:
                    continue
            
            # Verificar título de la página
            try:
                page_title = self.driver.title.lower()
                if any(term in page_title for term in ['mi cuenta', 'account', 'messages']):
                    return True
            except:
                pass
                
            print("❌ No se detectó sesión activa")
            return False
            
        except Exception as e:
            print(f"❌ Error verificando sesión: {e}")
            return False

    def _pedir_credenciales_interactivo(self, platform):
        """Pide credenciales al usuario de forma interactiva"""
        print(f"\n🔐 Credenciales necesarias para {platform.upper()}")
        print("Por favor, ingresa tus datos de acceso:")
        
        username = input("Usuario: ").strip()
        password = getpass.getpass("Contraseña: ").strip()
        
        if not username or not password:
            print("❌ Se requieren tanto usuario como contraseña")
            return False
        
        # Guardar credenciales
        if self.config_manager.set_credentials(platform, username, password):
            print("✅ Credenciales guardadas")
            # Intentar login nuevamente
            return self.login()
        else:
            print("❌ Error guardando credenciales")
            return False

    def _simplificar_nombre(self, nombre):
        """Simplifica el nombre de la carta eliminando comas y caracteres especiales"""
        if not nombre:
            return ""
        
        # Eliminar comas y apóstrofes, mantener solo letras, números y espacios
        nombre_simplificado = re.sub(r"[,']", "", nombre)
        nombre_simplificado = re.sub(r"[^\w\s]", " ", nombre_simplificado)
        nombre_simplificado = re.sub(r"\s+", " ", nombre_simplificado).strip()
        
        return nombre_simplificado
    
    def _coincide_nombre_simplificado(self, nombre_buscado, nombre_encontrado):
        """Compara si los nombres simplificados coinciden exactamente"""
        buscado_simplificado = self._simplificar_nombre(nombre_buscado).lower()
        encontrado_simplificado = self._simplificar_nombre(nombre_encontrado).lower()
        
        print(f"     🔍 Comparando: '{buscado_simplificado}' vs '{encontrado_simplificado}'")
        return buscado_simplificado == encontrado_simplificado
    
    def _tiene_numero_correcto(self, contenedor):
        """Verifica que la carta tenga un número normal (no alternativo)"""
        try:
            # Buscar el elemento que contiene el número
            numero_element = contenedor.find_element(By.CSS_SELECTOR, ".col-number span:last-child")
            numero_texto = numero_element.text.strip()
            
            # Verificar que sea un número puro (sin letras)
            if numero_texto and numero_texto.isdigit():
                print(f"     ✅ Número válido: #{numero_texto}")
                return True
            else:
                print(f"     ❌ Número inválido: '{numero_texto}'")
                return False
                
        except Exception as e:
            print(f"     ❌ No se pudo encontrar número: {e}")
            return False
    
    def _obtener_enlace_carta(self, contenedor):
        """Obtiene el enlace a la página de la carta - CORREGIDO"""
        try:
            # PRIMER INTENTO: Buscar el enlace dentro del contenedor principal
            enlace = contenedor.find_element(By.CSS_SELECTOR, "a[href*='/Singles/']")
            url_carta = enlace.get_attribute('href')
            print(f"     ✅ Enlace encontrado: {url_carta}")
            return url_carta
        except:
            try:
                # SEGUNDO INTENTO: Buscar cualquier enlace que contenga el nombre
                enlaces = contenedor.find_elements(By.TAG_NAME, "a")
                for enlace in enlaces:
                    href = enlace.get_attribute('href')
                    if href and '/Singles/' in href:
                        print(f"     ✅ Enlace encontrado (alternativo): {href}")
                        return href
            except:
                pass
        
        print("     ❌ No se pudo encontrar el enlace")
        return None
    
    def buscar_carta(self, nombre_carta):
        """Busca la carta en CardMarket usando la URL específica"""
        print(f"🔍 CardMarket: Iniciando búsqueda...")
        
        # CORRECCIÓN: Usar + en lugar de %2B para espacios
        nombre_codificado = nombre_carta.replace(' ', '+')
        url_busqueda = f"https://www.cardmarket.com/es/Magic/Products/Search?category=-1&searchString={nombre_codificado}&searchMode=v1"
        
        print(f"🌐 Navegando a: {url_busqueda}")
        self.driver.get(url_busqueda)
        time.sleep(5)
        
        print("✓ Página de búsqueda cargada")
        return True
    
    def seleccionar_carta_mas_barata(self, nombre_carta):
        """Selecciona la carta más barata en CardMarket que cumpla con los filtros"""
        try:
            print(f"🎯 CardMarket: Buscando '{nombre_carta}'...")
            
            # Esperar a que carguen los resultados
            time.sleep(3)
            
            # Buscar por el ID que contiene "productRow"
            contenedores_cartas = self.driver.find_elements(By.CSS_SELECTOR, "[id^='productRow']")
            print(f"📦 Encontrados {len(contenedores_cartas)} contenedores de cartas")
            
            cartas_encontradas = []
            
            for i, contenedor in enumerate(contenedores_cartas):
                try:
                    print(f"  🔍 Procesando carta {i+1}...")
                    
                    # FILTRO 1: Verificar que tenga número correcto
                    if not self._tiene_numero_correcto(contenedor):
                        continue
                    
                    # FILTRO 2: Extraer y comparar nombre
                    nombre_element = contenedor.find_element(By.CSS_SELECTOR, ".d-block.small.text-muted.fst-italic")
                    nombre_encontrado = nombre_element.text.strip()
                    print(f"     📝 Nombre encontrado: '{nombre_encontrado}'")
                    
                    # Verificar si coincide el nombre simplificado
                    if not self._coincide_nombre_simplificado(nombre_carta, nombre_encontrado):
                        print(f"     ❌ No coincide con '{nombre_carta}'")
                        continue
                    
                    print(f"     ✅ Coincide con '{nombre_carta}'")
                    
                    # FILTRO 3: Extraer precio
                    precio_element = contenedor.find_element(By.CSS_SELECTOR, ".col-price.pe-sm-2")
                    precio_texto = precio_element.text.strip()
                    print(f"     💰 Precio texto: '{precio_texto}'")
                    
                    # Limpiar y convertir precio
                    precio = self.utils.limpiar_y_convertir_precio_cardmarket(precio_texto)
                    
                    # CORRECCIÓN: Aceptar precios mayores a 0.01 en lugar de 0.10
                    if precio and precio >= 0.01:  # Cambiado de > 0.10 a >= 0.01
                        # Obtener el enlace usando el método corregido
                        url_carta = self._obtener_enlace_carta(contenedor)
                        
                        if url_carta:
                            cartas_encontradas.append({
                                'nombre': nombre_encontrado,
                                'precio': precio,
                                'url': url_carta,
                                'elemento': contenedor
                            })
                            print(f"     ✅ Añadida a la lista - Precio: €{precio:.2f}")
                        else:
                            print(f"     ❌ No se pudo obtener el enlace")
                    else:
                        print(f"     ❌ Precio no válido: {precio}")
                        
                except Exception as e:
                    print(f"     ⚠️ Error procesando carta {i+1}: {e}")
                    continue
            
            if not cartas_encontradas:
                print(f"❌ No se encontraron cartas que coincidan con '{nombre_carta}' y cumplan los filtros")
                return False
            
            # Ordenar por precio y seleccionar la más barata
            cartas_encontradas.sort(key=lambda x: x['precio'])
            carta_seleccionada = cartas_encontradas[0]
            
            print(f"✅ Carta seleccionada: {carta_seleccionada['nombre']}")
            print(f"💰 Precio: €{carta_seleccionada['precio']:.2f}")
            
            # Navegar a la página de la carta seleccionada
            print(f"🌐 Navegando a: {carta_seleccionada['url']}")
            self.driver.get(carta_seleccionada['url'])
            time.sleep(4)
            
            return True
            
        except Exception as e:
            print(f"❌ Error seleccionando carta en CardMarket: {e}")
            return False

    def buscar_vendedores(self, condiciones, cantidad_necesaria=1):
        """Busca vendedores en CardMarket con los nuevos filtros - MODIFICADO para priorizar stock"""
        print("🔍 CardMarket: Buscando vendedores con filtros...")
        
        try:
            # Esperar a que cargue la página de vendedores
            time.sleep(3)
            
            vendedores = []
            
            # Buscar todos los contenedores de vendedores
            contenedores_vendedores = self.driver.find_elements(By.CSS_SELECTOR, "[id^='articleRow']")
            print(f"📦 Encontrados {len(contenedores_vendedores)} contenedores de vendedores")
            
            for i, contenedor in enumerate(contenedores_vendedores):
                try:
                    print(f"  🔍 Procesando vendedor {i+1}...")
                    
                    # Extraer información del vendedor
                    info_vendedor = self._extraer_info_vendedor(contenedor)
                    
                    if not info_vendedor:
                        continue
                    
                    # APLICAR FILTROS
                    if not self._cumple_filtros(info_vendedor, condiciones):
                        continue
                    
                    # Buscar el botón de agregar al carrito
                    boton_agregar = self._obtener_boton_agregar(contenedor)
                    
                    if boton_agregar:
                        vendedores.append({
                            'vendedor': info_vendedor['nombre'],
                            'precio': info_vendedor['precio'],
                            'stock_disponible': info_vendedor['stock_disponible'],
                            'reputacion': info_vendedor['reputacion'],
                            'condicion': info_vendedor['condicion'],
                            'idioma': info_vendedor['idioma'],
                            'tiene_selector_cantidad': False,
                            'elemento_click_zero': boton_agregar,
                            'info_completa': info_vendedor
                        })
                        print(f"     ✅ Vendedor cumple filtros: {info_vendedor['nombre']} - €{info_vendedor['precio']:.2f} - Stock: {info_vendedor['stock_disponible']}")
                    else:
                        print(f"     ❌ No se pudo encontrar botón de agregar para {info_vendedor['nombre']}")
                        
                except Exception as e:
                    print(f"     ⚠️ Error procesando vendedor {i+1}: {e}")
                    continue
            
            # MODIFICACIÓN CRÍTICA: Ordenar por stock disponible (mayor a menor) y luego por precio
            if vendedores:
                print("📊 Ordenando vendedores por stock disponible (mayor a menor)...")
                vendedores.sort(key=lambda x: (
                    -x['stock_disponible'],  # Primero por stock (mayor a menor)
                    x['precio']  # Luego por precio (menor a mayor)
                ))
                
                # Mostrar el top 5 de vendedores por stock
                print("🏆 TOP 5 VENDEDORES POR STOCK DISPONIBLE:")
                for i, vendedor in enumerate(vendedores[:5]):
                    print(f"   {i+1}. {vendedor['vendedor']} - Stock: {vendedor['stock_disponible']} - Precio: €{vendedor['precio']:.2f}")
            
            print(f"🎯 Vendedores que cumplen filtros: {len(vendedores)}")
            return vendedores
            
        except Exception as e:
            print(f"❌ Error buscando vendedores en CardMarket: {e}")
            return []

    def _extraer_info_vendedor(self, contenedor):
        """Extrae la información completa de un vendedor - Asegurar que esté correctamente indentado"""
        try:
            info = {}
            
            # 1. Extraer NOMBRE del vendedor
            try:
                nombre_element = contenedor.find_element(By.CSS_SELECTOR, ".seller-name a")
                info['nombre'] = nombre_element.text.strip()
                print(f"     👤 Vendedor: {info['nombre']}")
            except:
                print("     ❌ No se pudo extraer nombre del vendedor")
                return None
            
            # 2. Extraer PRECIO - SELECTOR CORREGIDO
            try:
                # Intentar diferentes selectores para el precio
                selectores_precio = [
                    ".color-primary.small.text-end.text-nowrap.fw-bold",
                    ".color-primary.fw-bold",
                    ".text-end .color-primary",
                    "[class*='price']",
                    ".fw-bold"
                ]
                
                precio_encontrado = False
                for selector in selectores_precio:
                    try:
                        elementos_precio = contenedor.find_elements(By.CSS_SELECTOR, selector)
                        for elemento in elementos_precio:
                            precio_texto = elemento.text.strip()
                            if precio_texto and '€' in precio_texto:
                                info['precio'] = self.utils.limpiar_y_convertir_precio_cardmarket(precio_texto)
                                if info['precio'] and info['precio'] > 0:
                                    print(f"     💰 Precio: €{info['precio']:.2f} (selector: {selector})")
                                    precio_encontrado = True
                                    break
                        if precio_encontrado:
                            break
                    except:
                        continue
                
                if not precio_encontrado:
                    print("     ❌ No se pudo extraer precio con ningún selector")
                    return None
                    
            except Exception as e:
                print(f"     ❌ Error extrayendo precio: {e}")
                return None
            
            # 3. Extraer REPUTACIÓN
            try:
                # Buscar diferentes tipos de reputación
                reputaciones = [
                    "fonticon-seller-rating-outstanding",  # Sobresaliente
                    "fonticon-seller-rating-excellent",    # Excelente
                    "fonticon-seller-rating-good",         # Bueno
                    "fonticon-seller-rating-neutral",      # Neutral
                    "fonticon-seller-rating-poor"          # Pobre
                ]
                
                info['reputacion'] = "Desconocida"
                for reputacion in reputaciones:
                    try:
                        elemento = contenedor.find_element(By.CSS_SELECTOR, f".{reputacion}")
                        if elemento:
                            if "outstanding" in reputacion:
                                info['reputacion'] = "Sobresaliente"
                            elif "excellent" in reputacion:
                                info['reputacion'] = "Excelente"
                            elif "good" in reputacion:
                                info['reputacion'] = "Bueno"
                            elif "neutral" in reputacion:
                                info['reputacion'] = "Neutral"
                            elif "poor" in reputacion:
                                info['reputacion'] = "Pobre"
                            break
                    except:
                        continue
                
                print(f"     ⭐ Reputación: {info['reputacion']}")
            except:
                info['reputacion'] = "Desconocida"
                print("     ⚠️ No se pudo determinar reputación")
            
            # 4. Extraer STOCK DISPONIBLE
            try:
                # Buscar el tooltip que contiene la información de stock
                stock_element = contenedor.find_element(By.CSS_SELECTOR, ".sell-count")
                tooltip_text = stock_element.get_attribute("data-bs-original-title")
                
                if tooltip_text:
                    # Extraer el número de artículos disponibles del tooltip
                    # Formato: "5005 Ventas | 48525 Artículos disponibles"
                    patron_stock = r'(\d+)\s*Artículos disponibles'
                    match = re.search(patron_stock, tooltip_text)
                    if match:
                        info['stock_disponible'] = int(match.group(1))
                    else:
                        info['stock_disponible'] = 1  # Por defecto
                else:
                    info['stock_disponible'] = 1
                
                print(f"     📊 Stock disponible: {info['stock_disponible']}")
            except:
                info['stock_disponible'] = 1
                print("     ⚠️ No se pudo determinar stock, usando 1 por defecto")
            
            # 5. Extraer CONDICIÓN de la carta
            try:
                condicion_element = contenedor.find_element(By.CSS_SELECTOR, ".article-condition .badge")
                info['condicion'] = condicion_element.text.strip()
                print(f"     🎯 Condición: {info['condicion']}")
            except:
                info['condicion'] = "Desconocida"
                print("     ⚠️ No se pudo determinar condición")
            
            # 6. Extraer IDIOMA de la carta
            try:
                # Buscar la bandera de idioma (Inglés)
                bandera_ingles = contenedor.find_element(By.CSS_SELECTOR, "[aria-label='Inglés']")
                info['idioma'] = "Inglés"
                print(f"     🏴󠁧󠁢󠁥󠁮󠁧󠁿 Idioma: {info['idioma']}")
            except:
                info['idioma'] = "Desconocido"
                print("     ⚠️ No se pudo determinar idioma")
            
            return info
            
        except Exception as e:
            print(f"     ❌ Error extrayendo información del vendedor: {e}")
            return None

    def _cumple_filtros(self, info_vendedor, condiciones):
        """Verifica si el vendedor cumple con todos los filtros"""
        
        # FILTRO 1: Condición mínima NM (Near Mint)
        condiciones_aceptadas = ['NM']  # Solo Near Mint
        if info_vendedor['condicion'] not in condiciones_aceptadas:
            print(f"     ❌ Condición no aceptada: {info_vendedor['condicion']}")
            return False
        
        # FILTRO 2: Idioma Inglés
        if info_vendedor['idioma'] != "Inglés":
            print(f"     ❌ Idioma no aceptado: {info_vendedor['idioma']}")
            return False
        
        # FILTRO 3: Reputación mínima (opcional, pero buena práctica)
        reputaciones_aceptadas = ['Sobresaliente', 'Excelente', 'Bueno']
        if info_vendedor['reputacion'] not in reputaciones_aceptadas:
            print(f"     ❌ Reputación no aceptada: {info_vendedor['reputacion']}")
            return False
        
        # FILTRO 4: Precio máximo (si se especifica)
        precio_maximo = condiciones.get('precio_maximo', 1000)
        if info_vendedor['precio'] > precio_maximo:
            print(f"     ❌ Precio excede máximo: €{info_vendedor['precio']:.2f} > €{precio_maximo:.2f}")
            return False
        
        # FILTRO 5: Stock suficiente
        cantidad_necesaria = condiciones.get('cantidad_necesaria', 1)
        if info_vendedor['stock_disponible'] < cantidad_necesaria:
            print(f"     ❌ Stock insuficiente: {info_vendedor['stock_disponible']} < {cantidad_necesaria}")
            return False
        
        print("     ✅ Vendedor cumple todos los filtros")
        return True

    def _obtener_boton_agregar(self, contenedor):
        """Obtiene el botón de agregar al carrito"""
        try:
            # Buscar el botón de formulario (versión desktop)
            try:
                boton = contenedor.find_element(By.CSS_SELECTOR, "button[type='submit']")
                if boton.is_displayed() and "btn-primary" in boton.get_attribute("class"):
                    print("     ✅ Botón de agregar encontrado (desktop)")
                    return boton
            except:
                pass
            
            # Buscar el botón móvil (fallback)
            try:
                boton = contenedor.find_element(By.CSS_SELECTOR, ".mobile-cart.btn-primary")
                if boton.is_displayed():
                    print("     ✅ Botón de agregar encontrado (móvil)")
                    return boton
            except:
                pass
            
            # Buscar cualquier botón con icono de carrito
            try:
                botones = contenedor.find_elements(By.CSS_SELECTOR, ".btn-primary")
                for boton in botones:
                    if "cart" in boton.get_attribute("innerHTML").lower():
                        print("     ✅ Botón de agregar encontrado (genérico)")
                        return boton
            except:
                pass
            
            print("     ❌ No se pudo encontrar botón de agregar")
            return None
            
        except Exception as e:
            print(f"     ❌ Error buscando botón: {e}")
            return None
# Asegurar que las clases estén disponibles para importación
__all__ = ['PlatformBase', 'CardTraderPlatform', 'CardMarketPlatform']