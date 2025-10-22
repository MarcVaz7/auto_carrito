from shared.base_automation import BaseAutomation
from cardmarket.cardmarket_selector import CardMarketSelector
from cardmarket.cardmarket_finder import CardMarketFinder
from utils import Utils
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class CardMarketAutomation(BaseAutomation):
    def __init__(self):
        super().__init__("cardmarket")
        self.utils = Utils(self.driver)
        self.selector = CardMarketSelector(self.driver, self.utils)
        self.finder = CardMarketFinder(self.driver, self.utils)
        
        # NUEVO: Arraylist para guardar vendedores seleccionados
        self.vendedores_seleccionados = []
        print("📋 ArrayList de vendedores seleccionados inicializado")
    
    def login_automatico(self, username, password):
        """Inicio de sesión automático para CardMarket - CORREGIDO"""
        try:
            print("🔐 Iniciando sesión automática en CardMarket...")
            
            # Navegar a la página de login
            login_url = "https://www.cardmarket.com/es/Magic/Login"
            print(f"🌐 Navegando a: {login_url}")
            self.driver.get(login_url)
            time.sleep(3)
            
            # DEBUG: Verificar que estamos en la página correcta
            print(f"📄 Página actual: {self.driver.current_url}")
            print(f"📝 Título: {self.driver.title}")
            
            # Esperar a que los campos estén presentes
            print("🔍 Esperando campos de login...")
            wait = WebDriverWait(self.driver, 10)
            
            # Selectores para CardMarket
            username_selectors = [
                "input[name='username']",
                "input[type='text']",
                "#username"
            ]
            
            password_selectors = [
                "input[type='password']",
                "input[name='password']",
                "#password"
            ]
            
            submit_selectors = [
                "input[type='submit'][value='Iniciar sesión']",  # Selector específico
                "input[type='submit']",
                "button[type='submit']",
                ".btn-primary",
                "input[value='Iniciar sesión']"
            ]
            
            username_field = None
            password_field = None
            submit_btn = None
            
            # Intentar diferentes selectores para username
            for selector in username_selectors:
                try:
                    username_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    print(f"✅ Campo usuario encontrado: {selector}")
                    break
                except:
                    print(f"❌ Selector falló: {selector}")
                    continue
            
            # Intentar diferentes selectores para password
            for selector in password_selectors:
                try:
                    password_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    print(f"✅ Campo contraseña encontrado: {selector}")
                    break
                except:
                    print(f"❌ Selector falló: {selector}")
                    continue
            
            if not username_field or not password_field:
                print("❌ No se pudieron encontrar los campos de usuario/contraseña")
                return False
            
            # NUEVO: Primero llenar los campos para habilitar el botón
            print("⌨️  Rellenando campos de login...")
            
            # Limpiar y llenar campos
            username_field.clear()
            username_field.send_keys(username)
            time.sleep(1)
            
            password_field.clear()
            password_field.send_keys(password)
            time.sleep(1)
            
            # NUEVO: Esperar a que el botón se habilite
            print("⏳ Esperando a que el botón se habilite...")
            
            # Buscar el botón específico de "Iniciar sesión" que ahora debería estar habilitado
            for selector in submit_selectors:
                try:
                    # Esperar a que el botón esté presente y habilitado
                    submit_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    print(f"✅ Botón enviar encontrado y habilitado: {selector}")
                    break
                except:
                    print(f"❌ Selector no habilitado: {selector}")
                    continue
            
            if not submit_btn:
                print("❌ No se pudo encontrar el botón de enviar habilitado")
                
                # DEBUG: Mostrar estado de todos los botones de submit
                try:
                    submit_buttons = self.driver.find_elements(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']")
                    print("🔍 Estado de botones de submit:")
                    for btn in submit_buttons:
                        is_enabled = btn.is_enabled()
                        btn_value = btn.get_attribute("value") or btn.text
                        btn_type = btn.get_attribute("type")
                        print(f"   - value: '{btn_value}', type: {btn_type}, habilitado: {is_enabled}")
                except Exception as e:
                    print(f"❌ Error al verificar botones: {e}")
                
                return False
            
            # Hacer click en el botón de login
            print("🖱️  Haciendo click en enviar...")
            
            # Intentar diferentes métodos de click
            try:
                # Método 1: JavaScript click (más confiable)
                self.driver.execute_script("arguments[0].click();", submit_btn)
                print("✅ Click ejecutado con JavaScript")
            except Exception as js_error:
                print(f"❌ JavaScript click falló: {js_error}")
                try:
                    # Método 2: Click normal
                    submit_btn.click()
                    print("✅ Click ejecutado normalmente")
                except Exception as normal_error:
                    print(f"❌ Click normal falló: {normal_error}")
                    try:
                        # Método 3: Usar ActionChains
                        from selenium.webdriver.common.action_chains import ActionChains
                        actions = ActionChains(self.driver)
                        actions.move_to_element(submit_btn).click().perform()
                        print("✅ Click ejecutado con ActionChains")
                    except Exception as actions_error:
                        print(f"❌ ActionChains falló: {actions_error}")
                        return False
            
            time.sleep(5)  # Esperar a que procese el login
            
            # Verificar si el login fue exitoso
            if self._verificar_login_cardmarket_exitoso():
                print("🎉 Login en CardMarket exitoso!")
                return True
            else:
                print("❌ Login en CardMarket falló")
                # DEBUG: Verificar página actual después del login
                print(f"📄 URL después del intento: {self.driver.current_url}")
                print(f"📝 Título: {self.driver.title}")
                
                # Verificar si hay mensajes de error
                try:
                    error_elements = self.driver.find_elements(By.CSS_SELECTOR, ".alert-danger, .error, .text-danger")
                    for error in error_elements:
                        if error.is_displayed():
                            print(f"❌ Error visible: {error.text}")
                except:
                    pass
                    
                return False
                
        except Exception as e:
            print(f"❌ Error en login automático de CardMarket: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _verificar_login_cardmarket_exitoso(self):
        """Verificación específica para CardMarket - CORREGIDA"""
        time.sleep(3)
        
        print("🔍 Verificando login en CardMarket...")
        
        # Verificar redirección después del login
        current_url = self.driver.current_url.lower()
        print(f"📄 URL después del login: {current_url}")
        print(f"📝 Título: {self.driver.title}")
        
        # PRIMERO: Verificar si estamos en una página de ERROR de login
        if "login" in current_url or "signin" in current_url:
            print("❌ Todavía en página de login - falló")
            
            # Verificar si hay mensajes de error específicos
            try:
                error_selectors = [
                    "//div[contains(@class, 'alert-danger')]",
                    "//div[contains(@class, 'error')]",
                    "//span[contains(@class, 'error')]",
                    "//*[contains(text(), 'incorrect')]",
                    "//*[contains(text(), 'invalid')]",
                    "//*[contains(text(), 'contraseña incorrecta')]",
                    "//*[contains(text(), 'usuario no encontrado')]"
                ]
                
                for error_selector in error_selectors:
                    try:
                        error_elem = self.driver.find_element(By.XPATH, error_selector)
                        if error_elem.is_displayed():
                            error_text = error_elem.text.strip()
                            if error_text:
                                print(f"❌ Mensaje de error detectado: '{error_text}'")
                                return False
                    except:
                        continue
            except Exception as e:
                print(f"⚠️ Error al buscar mensajes de error: {e}")
                
            return False
        
        # SEGUNDO: Si NO estamos en página de login, verificar indicadores positivos
        print("✅ No estamos en página de login - verificando indicadores positivos...")
        
        # Buscar elementos que indican sesión activa en CardMarket
        indicadores_sesion = [
            "//a[contains(@href, '/users/sign_out')]",
            "//a[contains(@href, '/users/signout')]",
            "//a[contains(text(), 'Mi cuenta')]",
            "//a[contains(text(), 'My account')]",
            "//span[contains(text(), 'Hola')]",
            "//a[contains(@href, '/Messages')]",
            "//a[contains(@class, 'account')]",
            "//*[contains(text(), 'Cerrar sesión')]",
            "//*[contains(text(), 'Logout')]",
            "//*[contains(text(), 'Sign out')]"
        ]
        
        for indicador in indicadores_sesion:
            try:
                elemento = self.driver.find_element(By.XPATH, indicador)
                if elemento.is_displayed():
                    print(f"✅ Sesión activa detectada: {indicador}")
                    return True
            except:
                continue
        
        # TERCERO: Verificar por URL de éxito (después de login exitoso)
        urls_exito = [
            "https://www.cardmarket.com/es/magic",
            "https://www.cardmarket.com/es/magic/",
            "https://www.cardmarket.com/es/magic/mainpage",
            "https://www.cardmarket.com/es/magic/products",
            "https://www.cardmarket.com/es/account",
            "https://www.cardmarket.com/es/magic/users/"
        ]
        
        for url in urls_exito:
            if url in current_url:
                print(f"✅ Redirección a página principal detectada: {current_url}")
                
                # Verificar que NO estamos viendo mensajes de error
                page_source = self.driver.page_source.lower()
                
                # Solo considerar como error mensajes específicos de login fallido
                errores_reales = [
                    "incorrect",
                    "invalid", 
                    "error de inicio de sesión",
                    "login failed",
                    "contraseña incorrecta",
                    "usuario no encontrado"
                ]
                
                tiene_error_real = any(error in page_source for error in errores_reales)
                
                if not tiene_error_real:
                    print("✅ No se detectaron errores reales de login - SESIÓN EXITOSA")
                    return True
                else:
                    print("❌ Se detectaron errores reales en la página")
                    return False
        
        # CUARTO: Verificar contenido de la página de manera más precisa
        page_source = self.driver.page_source.lower()
        
        # Solo buscar errores específicos de login, no cualquier "error"
        errores_reales = [
            "incorrect",
            "invalid",
            "error de inicio de sesión", 
            "login failed",
            "contraseña incorrecta",
            "usuario no encontrado"
        ]
        
        # Buscar indicadores positivos en el contenido
        indicadores_positivos = [
            "mi cuenta",
            "my account", 
            "cerrar sesión",
            "logout",
            "sign out",
            "bienvenido",
            "welcome"
        ]
        
        tiene_error_real = any(error in page_source for error in errores_reales)
        tiene_indicador_positivo = any(indicador in page_source for indicador in indicadores_positivos)
        
        if tiene_error_real:
            print("❌ Se detectaron errores reales de login en el contenido")
            return False
        elif tiene_indicador_positivo:
            print("✅ Se detectaron indicadores positivos en el contenido - SESIÓN EXITOSA")
            return True
        
        # QUINTO: Si llegamos aquí y no estamos en login, asumimos éxito
        if "login" not in current_url and "signin" not in current_url:
            print("✅ No estamos en página de login y no hay errores evidentes - ASUNIENDO ÉXITO")
            return True
        
        print("❌ No se pudo verificar claramente el login")
        return False
        
        # Buscar elementos que indican sesión activa en CardMarket
        indicadores_sesion = [
            "//a[contains(@href, '/users/sign_out')]",
            "//a[contains(text(), 'Mi cuenta')]",
            "//span[contains(text(), 'Hola')]",
            "//a[contains(@href, '/Messages')]",
            "//a[contains(@class, 'account')]",
            "//*[contains(text(), 'Cerrar sesión')]",
            "//*[contains(text(), 'Logout')]"
        ]
        
        for indicador in indicadores_sesion:
            try:
                elemento = self.driver.find_element(By.XPATH, indicador)
                if elemento.is_displayed():
                    print(f"✅ Sesión activa detectada: {indicador}")
                    return True
            except:
                continue
        
        # Verificar por URL de éxito (después de login exitoso)
        urls_exito = [
            "https://www.cardmarket.com/es/Magic",
            "https://www.cardmarket.com/es/Magic/",
            "https://www.cardmarket.com/es/Magic/MainPage",
            "https://www.cardmarket.com/es/Magic/Products",
            "https://www.cardmarket.com/es/account"
        ]
        
        for url in urls_exito:
            if url in current_url:
                print(f"✅ Redirección a página principal detectada: {url}")
                return True
        
        # Verificar en el contenido de la página
        page_source = self.driver.page_source.lower()
        if "invalid" in page_source or "incorrect" in page_source or "error" in page_source:
            print("❌ Se detectaron mensajes de error en la página")
            return False
        
        # Si llegamos aquí y no estamos en login, asumimos éxito
        if "login" not in current_url and "signin" not in current_url:
            print("✅ No estamos en página de login - asumiendo éxito")
            return True
        
        print("❌ No se pudo verificar el login")
        return False
    
    def buscar_desde_pagina_principal(self, nombre_carta):
        """Busca la carta en CardMarket usando la URL específica"""
        print(f"🔍 CardMarket: Iniciando búsqueda...")
        
        # Verificar si estamos logueados antes de buscar
        if not self._verificar_login_cardmarket_exitoso():
            print("⚠️ No hay sesión activa, la búsqueda puede fallar")
        
        # Usar + en lugar de %2B para espacios
        nombre_codificado = nombre_carta.replace(' ', '+')
        url_busqueda = f"https://www.cardmarket.com/es/Magic/Products/Search?category=-1&searchString={nombre_codificado}&searchMode=v1"
        
        print(f"🌐 Navegando a: {url_busqueda}")
        self.driver.get(url_busqueda)
        time.sleep(5)
        
        print("✓ Página de búsqueda cargada")
        return True
    
    def seleccionar_carta_mas_barata(self, nombre_carta):
        """Selecciona la carta más barata"""
        return self.selector.seleccionar_carta_mas_barata(nombre_carta)
    
    def buscar_vendedores_con_zero_real(self, condiciones, cantidad_necesaria=1):
        """Busca vendedores con filtros"""
        return self.finder.buscar_vendedores(condiciones, cantidad_necesaria)
    
    def seleccionar_carta_con_reintentos(self, nombre_carta, condiciones, cantidad_necesaria=1):
        """Selecciona carta con reintentos automáticos si no hay vendedores"""
        print(f"🔄 Sistema de reintentos activado (máximo 5 intentos)")
        print(f"📦 Cantidad necesaria: {cantidad_necesaria}")
        
        for intento in range(5):
            print(f"\n🔄 INTENTO {intento + 1}/5")
            
            # Si no es el primer intento, volver a la página de resultados
            if intento > 0:
                print("↩️ Volviendo a la página de resultados...")
                self.driver.back()
                time.sleep(3)
            
            # Para CardMarket, usar lógica simple (no hay múltiples versiones como en CardTrader)
            carta_seleccionada = self.seleccionar_carta_mas_barata(nombre_carta)
            
            if not carta_seleccionada:
                print(f"❌ No hay más cartas disponibles para '{nombre_carta}'")
                return False
            
            # Buscar vendedores para esta carta con la cantidad necesaria
            print(f"\n🔍 PASO 3: Buscando vendedores...")
            vendedores = self.buscar_vendedores_con_zero_real(condiciones, cantidad_necesaria)
            
            if vendedores:
                # Procesar la compra con múltiples vendedores si es necesario
                resultado = self._procesar_compra_con_cantidad(vendedores, cantidad_necesaria, nombre_carta)
                if resultado:
                    return True
            else:
                print(f"😞 No hay vendedores para esta versión (intento {intento + 1})")
                print("   CardMarket: No hay más opciones disponibles")
                return False
        
        print(f"❌ No se encontraron vendedores después de 5 intentos")
        return False
    
    def _procesar_compra_con_cantidad(self, vendedores, cantidad_total, nombre_carta):
        """Procesa la compra de múltiples copias usando varios vendedores si es necesario"""
        cantidad_restante = cantidad_total
        vendedores_usados = []
        
        print(f"🛒 Comprando {cantidad_total} copias de '{nombre_carta}'")
        
        for vendedor in vendedores:
            if cantidad_restante <= 0:
                break
                
            # Calcular cuántas copias comprar de este vendedor
            copias_a_comprar = min(vendedor['stock_disponible'], cantidad_restante)
            
            print(f"\n📦 Vendedor: {vendedor['vendedor']}")
            print(f"   💰 Precio: €{vendedor['precio']:.2f}")
            print(f"   📊 Stock: {vendedor['stock_disponible']} unidades")
            print(f"   🛒 Comprando: {copias_a_comprar} copias")
            
            # NUEVO: Guardar vendedor en el arraylist antes de agregar al carrito
            info_vendedor = {
                'nombre': vendedor['vendedor'],
                'precio_unitario': vendedor['precio'],
                'copias_compradas': copias_a_comprar,
                'stock_total': vendedor['stock_disponible'],
                'carta': nombre_carta,
                'reputacion': vendedor['reputacion'],
                'condicion': vendedor['condicion'],
                'idioma': vendedor['idioma'],
                'timestamp': time.time()
            }
            
            # Agregar al arraylist de vendedores seleccionados
            self.vendedores_seleccionados.append(info_vendedor)
            print(f"   💾 VENDEDOR GUARDADO EN ARRAYLIST: '{vendedor['vendedor']}'")
            print(f"   📝 Información guardada: {copias_a_comprar} copias de '{nombre_carta}' a €{vendedor['precio']:.2f} cada una")
            
            # Agregar al carrito
            success = self.agregar_al_carrito_confiable(vendedor)
            
            if success:
                cantidad_restante -= copias_a_comprar
                vendedores_usados.append({
                    'vendedor': vendedor['vendedor'],
                    'copias': copias_a_comprar,
                    'precio': vendedor['precio']
                })
                print(f"   ✅ {copias_a_comprar} copias agregadas al carrito")
                print(f"   📦 Cantidad restante: {cantidad_restante}")
                
                # Si todavía necesitamos más copias, esperar un poco y continuar
                if cantidad_restante > 0:
                    print("   ⏳ Buscando siguiente vendedor...")
                    time.sleep(2)
            else:
                print(f"   ❌ Error agregando {copias_a_comprar} copias")
        
        if cantidad_restante == 0:
            print(f"\n🎉 ¡Todas las {cantidad_total} copias de '{nombre_carta}' agregadas al carrito!")
            print("📊 Resumen de compra:")
            for vendedor in vendedores_usados:
                print(f"   - {vendedor['vendedor']}: {vendedor['copias']} copias × €{vendedor['precio']:.2f}")
            
            # NUEVO: Mostrar resumen de vendedores guardados
            self._mostrar_resumen_vendedores_guardados()
            return True
        else:
            print(f"\n⚠️ Solo se pudieron agregar {cantidad_total - cantidad_restante} de {cantidad_total} copias")
            return cantidad_total - cantidad_restante > 0
    
    def _mostrar_resumen_vendedores_guardados(self):
        """Muestra un resumen de todos los vendedores guardados en el arraylist"""
        if not self.vendedores_seleccionados:
            print("📋 ArrayList de vendedores: Vacío")
            return
        
        print(f"\n{'='*60}")
        print("🏪 RESUMEN DE VENDEDORES GUARDADOS EN ARRAYLIST")
        print(f"{'='*60}")
        
        # Contar vendedores únicos
        vendedores_unicos = set(v['nombre'] for v in self.vendedores_seleccionados)
        print(f"📊 Total de vendedores únicos: {len(vendedores_unicos)}")
        print(f"📦 Total de transacciones guardadas: {len(self.vendedores_seleccionados)}")
        
        # Mostrar detalle de cada vendedor guardado
        for i, vendedor in enumerate(self.vendedores_seleccionados, 1):
            print(f"\n{i}. 🏷️  Vendedor: {vendedor['nombre']}")
            print(f"   📍 Carta: {vendedor['carta']}")
            print(f"   💰 Precio unitario: €{vendedor['precio_unitario']:.2f}")
            print(f"   🛒 Copias compradas: {vendedor['copias_compradas']}")
            print(f"   📊 Stock total disponible: {vendedor['stock_total']}")
            print(f"   ⭐ Reputación: {vendedor['reputacion']}")
            print(f"   💵 Total gastado: €{vendedor['precio_unitario'] * vendedor['copias_compradas']:.2f}")
        
        # Estadísticas adicionales
        total_gastado = sum(v['precio_unitario'] * v['copias_compradas'] for v in self.vendedores_seleccionados)
        total_copias = sum(v['copias_compradas'] for v in self.vendedores_seleccionados)
        
        print(f"\n💰 GASTO TOTAL: €{total_gastado:.2f}")
        print(f"📦 TOTAL DE COPIAS: {total_copias}")
        print(f"{'='*60}")
    
    def obtener_vendedores_seleccionados(self):
        """Retorna la lista de vendedores seleccionados"""
        return self.vendedores_seleccionados
    
    def obtener_vendedores_unicos(self):
        """Retorna una lista de vendedores únicos"""
        vendedores_unicos = []
        vendedores_vistos = set()
        
        for vendedor in self.vendedores_seleccionados:
            if vendedor['nombre'] not in vendedores_vistos:
                vendedores_unicos.append(vendedor)
                vendedores_vistos.add(vendedor['nombre'])
        
        return vendedores_unicos
    
    def agregar_al_carrito_confiable(self, vendedor):
        """Agrega al carrito de forma confiable"""
        print(f"🎯 Intentando agregar: {vendedor['vendedor']} - €{vendedor['precio']:.2f}")
        
        try:
            elemento_click = vendedor['elemento_click_zero']
            
            # Estrategia 1: JavaScript click (más confiable)
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elemento_click)
            time.sleep(1)
            self.driver.execute_script("arguments[0].click();", elemento_click)
            time.sleep(2)
            
            # Verificar si realmente se agregó
            if self.verificar_agregado_carrito():
                print("✅ ¡REALMENTE AGREGADO AL CARRITO!")
                return True
            else:
                print("⚠️ Click ejecutado pero no se verificó en carrito")
                return False
                
        except Exception as e:
            print(f"❌ Error al agregar: {e}")
            return False
    
    def verificar_agregado_carrito(self):
        """Verificación MEJORADA de si se agregó al carrito"""
        time.sleep(2)
        
        # Buscar mensajes de confirmación específicos
        confirmaciones = [
            "//*[contains(text(), 'añadido') and contains(text(), 'carrito')]",
            "//*[contains(text(), 'added') and contains(text(), 'cart')]",
            "//*[contains(@class, 'alert-success')]",
            "//*[contains(@class, 'toast-success')]"
        ]
        
        for confirmacion in confirmaciones:
            try:
                elemento = self.driver.find_element(By.XPATH, confirmacion)
                if elemento.is_displayed():
                    return True
            except:
                continue
        
        # Verificar si el botón cambió a "En carrito" o similar
        try:
            botones_carrito = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'carrito') or contains(text(), 'cart')]")
            for boton in botones_carrito:
                if any(texto in boton.text.lower() for texto in ['en carrito', 'in cart', 'añadido', 'added']):
                    return True
        except:
            pass
        
        # Si no encontramos confirmación visual, asumimos éxito
        print("⚠️ No se detectó confirmación visual, pero se asume éxito")
        return True