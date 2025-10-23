import time
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class CardMarketVendedor:
    def __init__(self, driver, utils):
        self.driver = driver
        self.utils = utils
        self.wait = WebDriverWait(driver, 10)
    
    def buscar_en_vendedor_prioritario(self, nombre_carta, vendedor, condiciones, cantidad_necesaria=1):
        """Busca una carta en un vendedor prioritario"""
        try:
            print(f"  🔍 Buscando '{nombre_carta}' en vendedor {vendedor['nombre']}...")
            
            # Construir URL de búsqueda en el vendedor
            nombre_carta_codificado = nombre_carta.replace(' ', '%20')
            url_busqueda = f"https://www.cardmarket.com/es/Magic/Users/{self._limpiar_nombre_vendedor(vendedor['nombre'])}/Offers/Singles?name={nombre_carta_codificado}&sortBy=name_asc"
            
            print(f"  🌐 Navegando a: {url_busqueda}")
            self.driver.get(url_busqueda)
            time.sleep(3)
            
            # Verificar si la página carga correctamente
            if "Users" not in self.driver.current_url:
                print(f"  ❌ Error cargando página del vendedor")
                return False
            
            # Buscar la carta en los resultados del vendedor
            carta_encontrada = self._buscar_carta_en_vendedor(nombre_carta, condiciones, cantidad_necesaria)
            
            if carta_encontrada:
                print(f"  ✅ Carta encontrada en vendedor {vendedor['nombre']}")
                return True
            else:
                print(f"  ❌ Carta no encontrada en vendedor {vendedor['nombre']}")
                return False
                
        except Exception as e:
            print(f"  ❌ Error buscando en vendedor prioritario: {e}")
            return False

    def _buscar_carta_en_vendedor(self, nombre_carta, condiciones, cantidad_necesaria=1):
        """Busca una carta específica en la página de ofertas del vendedor"""
        try:
            # Esperar a que carguen los resultados
            time.sleep(3)
            
            # Buscar todos los artículos del vendedor
            articulos = self.driver.find_elements(By.CSS_SELECTOR, "[id^='articleRow']")
            print(f"  📦 Encontrados {len(articulos)} artículos del vendedor")
            
            cartas_validas = []
            
            for i, articulo in enumerate(articulos):
                try:
                    print(f"    🔍 Procesando artículo {i+1}...")
                    
                    # FILTRO 1: Nombre exacto de la carta
                    if not self._cumple_filtro_nombre_vendedor(articulo, nombre_carta):
                        continue
                    
                    # FILTRO 2: Condición NM
                    if not self._cumple_filtro_condicion_vendedor(articulo):
                        continue
                    
                    # FILTRO 3: Idioma Inglés
                    if not self._cumple_filtro_idioma_vendedor(articulo):
                        continue
                    
                    # FILTRO 4: Precio válido
                    precio = self._extraer_precio_vendedor(articulo)
                    if not precio or precio > condiciones.get('precio_maximo', 1000):
                        continue
                    
                    # FILTRO 5: Stock suficiente
                    stock = self._extraer_stock_vendedor(articulo)
                    if stock < cantidad_necesaria:
                        continue
                    
                    # Si pasa todos los filtros, es válida
                    cartas_validas.append({
                        'articulo': articulo,
                        'precio': precio,
                        'stock': stock
                    })
                    print(f"    ✅ Artículo cumple todos los filtros - €{precio:.2f}")
                    
                except Exception as e:
                    print(f"    ⚠️ Error procesando artículo: {e}")
                    continue
            
            if not cartas_validas:
                print("    ❌ No hay artículos que cumplan los filtros")
                return False
            
            # Seleccionar el más barato
            cartas_validas.sort(key=lambda x: x['precio'])
            carta_seleccionada = cartas_validas[0]
            
            print(f"    ✅ Artículo seleccionado - €{carta_seleccionada['precio']:.2f}")
            
            # Agregar al carrito
            return self._agregar_al_carrito_vendedor(carta_seleccionada['articulo'])
            
        except Exception as e:
            print(f"  ❌ Error buscando carta en vendedor: {e}")
            return False

    def _cumple_filtro_nombre_vendedor(self, articulo, nombre_carta):
        """Verifica que el artículo tenga el nombre correcto comparando con el href"""
        try:
            enlace = articulo.find_element(By.CSS_SELECTOR, "a[href*='/Singles/']")
            href = enlace.get_attribute('href')
            
            # Extraer la parte final del href (el nombre de la carta en inglés)
            # Ejemplo: "/es/Magic/Products/Singles/Commander-Tarkir-Dragonstorm/Sol-Ring" -> "Sol-Ring"
            partes_href = href.split('/')
            nombre_href = partes_href[-1] if partes_href else ""
            
            # Simplificar nombres para comparación
            nombre_buscado_simplificado = self._simplificar_nombre_href(nombre_carta)
            nombre_encontrado_simplificado = self._simplificar_nombre_href(nombre_href)
            
            coincide = nombre_buscado_simplificado == nombre_encontrado_simplificado
            
            if not coincide:
                print(f"      ❌ Nombre no coincide: '{nombre_href}' (buscado: '{nombre_carta}')")
            else:
                print(f"      ✅ Nombre coincide: '{nombre_href}'")
            
            return coincide
            
        except Exception as e:
            print(f"      ❌ Error verificando nombre: {e}")
            return False

    def _simplificar_nombre_href(self, nombre):
        """Simplifica el nombre del href para comparación"""
        if not nombre:
            return ""
        
        # Convertir a minúsculas
        nombre_simplificado = nombre.lower()
        
        # Reemplazar guiones por espacios (ej: "Sol-Ring" -> "sol ring")
        nombre_simplificado = nombre_simplificado.replace('-', ' ')
        
        # Eliminar caracteres especiales y espacios múltiples
        nombre_simplificado = re.sub(r'[^\w\s]', '', nombre_simplificado)
        nombre_simplificado = re.sub(r'\s+', ' ', nombre_simplificado).strip()
        
        return nombre_simplificado

    def _cumple_filtro_condicion_vendedor(self, articulo):
        """Verifica que la condición sea NM"""
        try:
            condicion_element = articulo.find_element(By.CSS_SELECTOR, ".article-condition .badge")
            condicion = condicion_element.text.strip()
            
            if condicion == "NM":
                return True
            else:
                print(f"      ❌ Condición no NM: {condicion}")
                return False
                
        except Exception as e:
            print(f"      ❌ Error verificando condición: {e}")
            return False

    def _cumple_filtro_idioma_vendedor(self, articulo):
        """Verifica que el idioma sea Inglés"""
        try:
            # Buscar la bandera de inglés
            bandera_ingles = articulo.find_element(By.CSS_SELECTOR, "[aria-label='Inglés']")
            return True
        except:
            try:
                # Buscar por estilo de background (fallback)
                banderas = articulo.find_elements(By.CSS_SELECTOR, "[style*='background-position']")
                for bandera in banderas:
                    estilo = bandera.get_attribute("style")
                    if "-16px -0px" in estilo:  # Posición de bandera UK
                        return True
            except:
                pass
            
            print("      ❌ Idioma no es Inglés")
            return False

    def _extraer_precio_vendedor(self, articulo):
        """Extrae el precio del artículo del vendedor"""
        try:
            # Intentar diferentes selectores de precio
            selectores_precio = [
                ".color-primary.fw-bold",
                ".color-primary.small.text-end.text-nowrap.fw-bold",
                "[class*='price']"
            ]
            
            for selector in selectores_precio:
                try:
                    precio_element = articulo.find_element(By.CSS_SELECTOR, selector)
                    precio_texto = precio_element.text.strip()
                    precio = self.utils.limpiar_y_convertir_precio_cardmarket(precio_texto)
                    if precio:
                        return precio
                except:
                    continue
            
            return None
        except:
            return None

    def _extraer_stock_vendedor(self, articulo):
        """Extrae el stock disponible del artículo"""
        try:
            stock_element = articulo.find_element(By.CSS_SELECTOR, ".item-count")
            return int(stock_element.text.strip())
        except:
            return 1  # Por defecto

    def _agregar_al_carrito_vendedor(self, articulo):
        """Agrega el artículo del vendedor al carrito"""
        try:
            # Buscar el botón de agregar al carrito (versión desktop)
            boton = articulo.find_element(By.CSS_SELECTOR, "button[type='submit']")
            
            # Hacer click con JavaScript
            self.driver.execute_script("arguments[0].click();", boton)
            time.sleep(2)
            
            # Verificar si se agregó correctamente
            if self._verificar_agregado_carrito_vendedor():
                print("      ✅ ¡Agregado al carrito correctamente!")
                return True
            else:
                print("      ❌ No se pudo verificar la adición al carrito")
                return False
                
        except Exception as e:
            print(f"      ❌ Error agregando al carrito: {e}")
            return False

    def _verificar_agregado_carrito_vendedor(self):
        """Verificación específica para agregado desde página de vendedor"""
        time.sleep(2)
        
        # Buscar mensajes de confirmación
        confirmaciones = [
            "//*[contains(text(), 'añadido') and contains(text(), 'carrito')]",
            "//*[contains(text(), 'added') and contains(text(), 'cart')]",
            "//*[contains(@class, 'alert-success')]"
        ]
        
        for confirmacion in confirmaciones:
            try:
                elemento = self.driver.find_element(By.XPATH, confirmacion)
                if elemento.is_displayed():
                    return True
            except:
                continue
        
        # Si no encontramos confirmación visual, asumimos éxito
        print("      ⚠️ No se detectó confirmación visual, pero se asume éxito")
        return True

    def _limpiar_nombre_vendedor(self, nombre_vendedor):
        """Limpia el nombre del vendedor para usarlo en la URL"""
        try:
            # Convertir a minúsculas
            nombre_limpio = nombre_vendedor.lower()
            
            # Reemplazar espacios por guiones
            nombre_limpio = nombre_limpio.replace(' ', '-')
            
            # Eliminar caracteres especiales (mantener solo letras, números y guiones)
            nombre_limpio = re.sub(r'[^a-z0-9-]', '', nombre_limpio)
            
            # Eliminar guiones múltiples consecutivos
            nombre_limpio = re.sub(r'-+', '-', nombre_limpio)
            
            # Eliminar guiones al inicio y final
            nombre_limpio = nombre_limpio.strip('-')
            
            print(f"   🔄 Nombre limpiado: '{nombre_vendedor}' -> '{nombre_limpio}'")
            return nombre_limpio
            
        except Exception as e:
            print(f"   ❌ Error limpiando nombre del vendedor: {e}")
            # Fallback: reemplazar espacios simples
            return nombre_vendedor.replace(' ', '-')

    def _simplificar_nombre(self, nombre):
        """Simplifica el nombre de la carta (método auxiliar)"""
        if not nombre:
            return ""
        
        nombre_simplificado = re.sub(r"[,']", "", nombre)
        nombre_simplificado = re.sub(r"[^\w\s]", " ", nombre_simplificado)
        nombre_simplificado = re.sub(r"\s+", " ", nombre_simplificado).strip()
        
        return nombre_simplificado

    def abrir_pagina_vendedor(self, nombre_vendedor):
        """Abre la página de ofertas del vendedor en una nueva pestaña"""
        try:
            # Limpiar el nombre del vendedor para la URL
            nombre_limpio = self._limpiar_nombre_vendedor(nombre_vendedor)
            
            # Construir la URL del vendedor
            url_vendedor = f"https://www.cardmarket.com/es/Magic/Users/{nombre_limpio}/Offers/Singles"
            
            print(f"   🌐 Abriendo página del vendedor: {url_vendedor}")
            
            # Abrir en nueva pestaña
            self.driver.execute_script(f"window.open('{url_vendedor}', '_blank');")
            
            # Cambiar a la nueva pestaña
            self.driver.switch_to.window(self.driver.window_handles[-1])
            time.sleep(3)
            
            print(f"   ✅ Página del vendedor abierta correctamente")
            
            # Volver a la pestaña anterior (la del carrito)
            self.driver.close()  # Cerrar la pestaña del vendedor
            self.driver.switch_to.window(self.driver.window_handles[0])
            time.sleep(1)
            
        except Exception as e:
            print(f"   ❌ Error al abrir página del vendedor: {e}")
            # Asegurarse de volver a la pestaña principal
            try:
                self.driver.switch_to.window(self.driver.window_handles[0])
            except:
                pass