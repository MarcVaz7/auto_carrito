from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time
import re
import urllib.parse

class CardTraderAutomationFinal:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("detach", True)
        self.service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        self.actions = ActionChains(self.driver)
    
    def cerrar_popups(self):
        """Cierra todos los popups molestos"""
        try:
            popup_selectors = [
                ".iubenda-cs-close-btn",
                "button[iubenda-cc-close]",
                "#iubenda-cs-banner button",
            ]
            
            for selector in popup_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            element.click()
                            time.sleep(0.5)
                except:
                    continue
                    
            # JavaScript adicional para asegurar
            self.driver.execute_script("""
                var closeButtons = document.querySelectorAll('.iubenda-cs-close-btn, [iubenda-cc-close]');
                closeButtons.forEach(function(btn) { if(btn) btn.click(); });
            """)
        except Exception as e:
            print(f"ℹ️ No se pudieron cerrar popups: {e}")
    
    def buscar_desde_pagina_principal(self, nombre_carta):
        """Busca la carta desde la página principal usando el buscador ManaSearch"""
        print(f"🔍 Iniciando búsqueda desde página principal...")
        
        # Ir a la página principal de Magic
        url_principal = "https://www.cardtrader.com/es/magic"
        self.driver.get(url_principal)
        time.sleep(5)
        self.cerrar_popups()
        
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
        """Selecciona la carta más barata de los resultados"""
        try:
            print("🎯 Analizando resultados de búsqueda...")
            
            cartas_encontradas = []
            
            # ESTRATEGIA: Buscar enlaces de cartas en los resultados
            enlaces_cartas = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/cards/']")
            print(f"🔗 Enlaces de cartas encontrados: {len(enlaces_cartas)}")
            
            for enlace in enlaces_cartas[:40]:  # Revisar primeros 40 enlaces
                try:
                    texto = enlace.text.strip()
                    href = enlace.get_attribute('href')
                    
                    if not texto or len(texto) < 3:
                        continue
                    
                    # Buscar el contenedor completo de la carta
                    contenedor = self._encontrar_contenedor_carta(enlace)
                    if contenedor:
                        carta = self._extraer_carta_desde_contenedor(contenedor, nombre_carta)
                        if carta and carta['precio'] > 0.10:  # Precio mínimo razonable
                            cartas_encontradas.append(carta)
                            print(f"  ✅ {carta['nombre'][:35]}... - €{carta['precio']:.2f}")
                except:
                    continue
            
            # Estrategia alternativa si no encontramos suficientes cartas
            if len(cartas_encontradas) < 3:
                cartas_encontradas.extend(self._busqueda_alternativa_cartas(nombre_carta))
            
            print(f"🎯 Cartas válidas encontradas: {len(cartas_encontradas)}")
            
            if not cartas_encontradas:
                print("❌ No se encontraron cartas que coincidan")
                return False
            
            # Mostrar opciones
            print(f"\n📊 CARTAS ENCONTRADAS:")
            for i, carta in enumerate(cartas_encontradas, 1):
                print(f"  {i}. {carta['nombre']} - €{carta['precio']:.2f}")
            
            # Seleccionar la más barata
            cartas_encontradas.sort(key=lambda x: x['precio'])
            carta_seleccionada = cartas_encontradas[0]
            
            print(f"\n🎯 CARTA SELECCIONADA:")
            print(f"   📦 {carta_seleccionada['nombre']}")
            print(f"   💰 €{carta_seleccionada['precio']:.2f}")
            
            # Navegar a la carta seleccionada
            print("🔄 Navegando a la página de la carta...")
            self.driver.get(carta_seleccionada['url'])
            time.sleep(4)
            return True
            
        except Exception as e:
            print(f"❌ Error en selección: {e}")
            return False
    
    def _encontrar_contenedor_carta(self, enlace):
        """Encuentra el contenedor completo de una carta"""
        try:
            for i in range(1, 4):
                try:
                    contenedor = enlace.find_element(By.XPATH, f"./ancestor::*[{i}]")
                    texto = contenedor.text.strip()
                    if texto and '€' in texto and len(texto) > 50:
                        return contenedor
                except:
                    continue
            return enlace
        except:
            return enlace
    
    def _extraer_carta_desde_contenedor(self, contenedor, nombre_carta):
        """Extrae información de carta desde un contenedor"""
        try:
            texto = contenedor.text.strip()
            if not texto or len(texto) < 20:
                return None
            
            carta = {}
            
            # Extraer nombre
            lineas = [l.strip() for l in texto.split('\n') if l.strip()]
            for linea in lineas:
                if self._coincidencia_flexible(linea, nombre_carta) and len(linea) > 5:
                    carta['nombre'] = linea
                    break
            
            if 'nombre' not in carta:
                for linea in lineas:
                    if len(linea) > 5 and not any(x in linea for x in ['€', 'Añadir', 'Add']):
                        carta['nombre'] = linea
                        break
            
            if 'nombre' not in carta:
                return None
            
            # Extraer URL
            try:
                enlaces = contenedor.find_elements(By.TAG_NAME, "a")
                for enlace in enlaces:
                    href = enlace.get_attribute('href')
                    if href and '/cards/' in href:
                        carta['url'] = href
                        break
                if 'url' not in carta:
                    return None
            except:
                return None
            
            # Extraer precio
            carta['precio'] = 0.0
            matches = re.findall(r'€\s*([0-9]+[.,][0-9]+)', texto)
            if matches:
                precios = [float(m.replace(',', '.')) for m in matches]
                precios_validos = [p for p in precios if p > 0.10]
                if precios_validos:
                    carta['precio'] = min(precios_validos)
                else:
                    carta['precio'] = min(precios)
            
            return carta
            
        except:
            return None
    
    def _busqueda_alternativa_cartas(self, nombre_carta):
        """Búsqueda alternativa de cartas"""
        cartas = []
        try:
            elementos_carta = self.driver.find_elements(By.CSS_SELECTOR, ".blueprint-card, .product, [class*='card']")
            for elemento in elementos_carta[:25]:
                try:
                    texto = elemento.text.strip()
                    if texto and len(texto) > 20 and self._coincidencia_flexible(texto, nombre_carta):
                        carta = self._extraer_carta_desde_contenedor(elemento, nombre_carta)
                        if carta and carta['precio'] > 0.10:
                            cartas.append(carta)
                except:
                    continue
        except:
            pass
        return cartas
    
    def _coincidencia_flexible(self, texto, busqueda):
        """Coincidencia flexible del nombre"""
        texto_limpio = texto.lower()
        busqueda_limpia = busqueda.lower()
        
        if busqueda_limpia in texto_limpio:
            return True
        
        palabras_busqueda = [p for p in re.findall(r'\w+', busqueda_limpia) if len(p) > 3]
        palabras_texto = [p for p in re.findall(r'\w+', texto_limpio) if len(p) > 3]
        
        if not palabras_busqueda:
            return False
        
        coincidencias = sum(1 for pb in palabras_busqueda if any(pt == pb for pt in palabras_texto))
        return coincidencias >= len(palabras_busqueda) * 0.6

    def buscar_vendedores_con_zero_real(self, condiciones):
        """Busca SOLO vendedores que tengan botón Zero REAL y cumplan filtros de ubicación e idioma"""
        print("🔍 Analizando vendedores en la página de la carta...")
        
        self.cerrar_popups()
        
        try:
            # Buscar TODAS las celdas Zero
            celdas_zero = self.driver.find_elements(By.CSS_SELECTOR, ".products-table__zero")
            print(f"📦 Celdas Zero encontradas: {len(celdas_zero)}")
            
            vendedores_con_zero_real = []
            vendedores_rechazados = []
            
            for i, celda_zero in enumerate(celdas_zero):
                try:
                    # Encontrar la fila padre de esta celda Zero
                    fila = celda_zero.find_element(By.XPATH, "./ancestor::tr[1]")
                    
                    # Verificar si esta celda Zero tiene contenido REAL (botón o elemento clickeable)
                    elementos_interiores = celda_zero.find_elements(By.XPATH, ".//*")
                    tiene_contenido_real = len(elementos_interiores) > 0
                    
                    # Solo procesar si tiene contenido REAL
                    if tiene_contenido_real:
                        info = self._extraer_info_vendedor_completo(fila, celda_zero)
                        if info and info['precio'] > 0:
                            # DEBUG: Mostrar información del vendedor
                            print(f"  🔍 Analizando vendedor {i+1}: {info['vendedor']} - €{info['precio']:.2f}")
                            print(f"     📍 Ubicación: {info['paises']}")
                            print(f"     🏷️  Condición: {info['condicion']}")
                            print(f"     🗣️  Idioma: {info['idioma']}")
                            
                            # Aplicar filtros de ubicación e idioma
                            if self._cumple_filtros_ubicacion_idioma(info):
                                vendedores_con_zero_real.append(info)
                                print(f"  ✅ Vendedor {i+1}: {info['vendedor']} - €{info['precio']:.2f} - CUMPLE FILTROS")
                            else:
                                razon = self._obtener_razon_rechazo(info)
                                vendedores_rechazados.append(info)
                                print(f"  ❌ Vendedor {i+1}: {info['vendedor']} - €{info['precio']:.2f} - {razon}")
                    else:
                        vendedor_texto = fila.text.split('\n')[0] if fila.text else "Desconocido"
                        print(f"  ❌ Vendedor {i+1}: {vendedor_texto} - Zero VACÍO (sin stock)")
                        
                except Exception as e:
                    continue
            
            print(f"🎯 Vendedores que cumplen filtros UE (sin UK) + Inglés: {len(vendedores_con_zero_real)}")
        
            # Aplicar filtros adicionales (condición, precio máximo)
            vendedores_filtrados = self._aplicar_filtros_avanzados(vendedores_con_zero_real, condiciones)
            
            # ORDENAR por precio (más bajo primero)
            vendedores_filtrados.sort(key=lambda x: x['precio'])
            
            # DEBUG: Mostrar orden final
            if vendedores_filtrados:
                print(f"\n📊 ORDEN FINAL DE VENDEDORES:")
                for i, vendedor in enumerate(vendedores_filtrados, 1):
                    paises = ', '.join(vendedor['paises']) if vendedor['paises'] else 'No especificado'
                    print(f"  {i}. {vendedor['vendedor']} - €{vendedor['precio']:.2f} - {vendedor['condicion']} - {vendedor['idioma']}")
                    print(f"     📍 {paises}")
            
            return vendedores_filtrados
            
        except Exception as e:
            print(f"❌ Error en búsqueda: {e}")
            return []
    
    def _extraer_info_vendedor_completo(self, fila, celda_zero):
        """Extrae información completa del vendedor con Zero real"""
        try:
            info = {}
            
            # Extraer nombre del vendedor
            try:
                vendedor_elem = fila.find_element(By.CSS_SELECTOR, ".products-table__seller")
                info['vendedor'] = vendedor_elem.text
            except:
                info['vendedor'] = "Desconocido"
            
            # Extraer precio
            try:
                precio_elem = fila.find_element(By.CSS_SELECTOR, ".products-table__formatted-price")
                precio_texto = precio_elem.text
                match = re.search(r'€\s*([0-9]+[.,][0-9]+)', precio_texto)
                if match:
                    info['precio'] = float(match.group(1).replace(',', '.'))
                else:
                    info['precio'] = 0.0
            except:
                info['precio'] = 0.0
            
            # Información de Zero (ESTA CELDA SÍ TIENE CONTENIDO)
            info['tiene_zero_real'] = True
            info['celda_zero'] = celda_zero
            
            # Buscar el elemento clickeable dentro de Zero
            try:
                # Primero buscar botón
                boton = celda_zero.find_element(By.TAG_NAME, "button")
                info['elemento_click_zero'] = boton
            except:
                try:
                    # Si no hay botón, buscar cualquier elemento clickeable
                    elementos_clickeables = celda_zero.find_elements(By.XPATH, ".//*")
                    if elementos_clickeables:
                        info['elemento_click_zero'] = elementos_clickeables[0]
                    else:
                        info['elemento_click_zero'] = celda_zero
                except:
                    info['elemento_click_zero'] = celda_zero
            
            # Extraer condición - BUSCAR EXACTAMENTE COMO EN EL HTML
            try:
                # Buscar el badge de condición NM
                condicion_elem = fila.find_element(By.CSS_SELECTOR, ".badge-cond-near-mint, .products-table__info--condition")
                info['condicion'] = condicion_elem.text
            except:
                info['condicion'] = "Desconocida"
            
            # Extraer UBICACIÓN del vendedor - bandera ES
            info['paises'] = []
            try:
                # Buscar banderas de ubicación (primera bandera en el seller)
                banderas_ubicacion = fila.find_elements(By.CSS_SELECTOR, ".products-table__seller .flag-icon")
                for bandera in banderas_ubicacion:
                    clase = bandera.get_attribute('class')
                    if 'flag-icon-es' in clase:
                        info['paises'].append('España')
                    elif 'flag-icon-fr' in clase:
                        info['paises'].append('Francia')
                    elif 'flag-icon-de' in clase:
                        info['paises'].append('Alemania')
                    elif 'flag-icon-it' in clase:
                        info['paises'].append('Italia')
                    elif 'flag-icon-pt' in clase:
                        info['paises'].append('Portugal')
                    elif 'flag-icon-nl' in clase:
                        info['paises'].append('Países Bajos')
                    elif 'flag-icon-gb' in clase:
                        info['paises'].append('Reino Unido')
            except:
                pass
            
            # Extraer IDIOMA de la carta - bandera EN específica
            info['idioma'] = "Desconocido"
            try:
                # Buscar específicamente la bandera de idioma en products-table__info--language
                bandera_idioma = fila.find_element(By.CSS_SELECTOR, ".products-table__info--language .flag-icon-prop.flag-icon-en")
                info['idioma'] = "Inglés"
            except:
                try:
                    # Alternativa: buscar cualquier bandera EN en la sección de idioma
                    banderas_idioma = fila.find_elements(By.CSS_SELECTOR, ".products-table__info--language .flag-icon")
                    for bandera in banderas_idioma:
                        clase = bandera.get_attribute('class')
                        if 'flag-icon-en' in clase:
                            info['idioma'] = "Inglés"
                            break
                except:
                    pass
            
            info['fila'] = fila
            return info
            
        except Exception as e:
            print(f"⚠️ Error extrayendo info: {e}")
            return None
    
    def _cumple_filtros_ubicacion_idioma(self, info_vendedor):
        """Verifica si el vendedor cumple con los filtros de ubicación (UE sin UK) e idioma (Inglés)"""
        # PAÍSES UE ACEPTADOS (EXCLUYENDO UK)
        paises_ue_aceptados = ['España', 'Francia', 'Alemania', 'Italia', 'Portugal', 'Países Bajos']
        paises_rechazados = ['Reino Unido']
        
        # VERIFICAR FILTROS:
        # 1. Ubicación debe ser UE (y NO UK)
        ubicacion_valida = any(pais in info_vendedor['paises'] for pais in paises_ue_aceptados)
        
        # 2. Idioma debe ser inglés
        idioma_valido = info_vendedor['idioma'] == "Inglés"
        
        # 3. NO debe estar en países rechazados
        ubicacion_rechazada = any(pais in info_vendedor['paises'] for pais in paises_rechazados)
        no_rechazado = not ubicacion_rechazada
        
        # 4. Condición debe ser NM
        condicion_valida = info_vendedor['condicion'] == "NM"
        
        return ubicacion_valida and idioma_valido and no_rechazado and condicion_valida

    def _obtener_razon_rechazo(self, info_vendedor):
        """Obtiene la razón por la que un vendedor fue rechazado"""
        paises_ue_aceptados = ['España', 'Francia', 'Alemania', 'Italia', 'Portugal', 'Países Bajos']
        paises_rechazados = ['Reino Unido']
        
        # Verificar ubicación
        ubicacion_ue = any(pais in info_vendedor['paises'] for pais in paises_ue_aceptados)
        ubicacion_rechazada = any(pais in info_vendedor['paises'] for pais in paises_rechazados)
        
        # Verificar idioma
        idioma_ingles = info_vendedor['idioma'] == "Inglés"
        
        # Verificar condición
        condicion_nm = info_vendedor['condicion'] == "NM"
        
        # Determinar razón
        if ubicacion_rechazada:
            return "Ubicación UK (excluido)"
        elif not ubicacion_ue:
            return f"Ubicación no UE: {info_vendedor['paises']}"
        elif not idioma_ingles:
            return f"Idioma no inglés ({info_vendedor['idioma']})"
        elif not condicion_nm:
            return f"Condición no NM ({info_vendedor['condicion']})"
        else:
            return "Razón desconocida"
    
    def _aplicar_filtros_avanzados(self, vendedores, condiciones):
        """Aplica filtros avanzados"""
        vendedores_filtrados = []
        
        for vendedor in vendedores:
            cumple_condiciones = True
            
            # Filtro de precio máximo
            if vendedor['precio'] > condiciones.get('precio_maximo', 1000):
                print(f"  ❌ {vendedor['vendedor']} - Precio demasiado alto: €{vendedor['precio']:.2f}")
                cumple_condiciones = False
                continue
            
            if cumple_condiciones:
                vendedores_filtrados.append(vendedor)
        
        return vendedores_filtrados
    
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
        """Verificación MÁS ESTRICTA de si se agregó al carrito"""
        time.sleep(3)
        
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
                    print(f"✅ Confirmación visual: {elemento.text[:100]}")
                    return True
            except:
                continue
        
        # Verificar cambio en el icono del carrito
        try:
            icono_carrito = self.driver.find_element(By.CSS_SELECTOR, ".fa-shopping-cart, .shopping-cart")
            # Tomar screenshot para debug
            self.driver.save_screenshot("debug_carrito.png")
            print("📸 Screenshot guardado como 'debug_carrito.png'")
        except:
            pass
        
        print("❌ No se detectó confirmación de agregado al carrito")
        return False
    
    def mantener_abierto(self):
        """Mantiene el navegador abierto"""
        print("\n🖥️ Navegador permanece abierto...")
        input("Presiona Enter para cerrar...")
    
    def cerrar(self):
        """Cierra el navegador"""
        self.driver.quit()

# PROGRAMA PRINCIPAL COMBINADO
def main():
    automator = CardTraderAutomationFinal()
    
    try:
        print("🚀 AUTOMATIZACIÓN CARDTRADER - VERSIÓN CON FILTROS ESTRICTOS")
        print("=" * 60)
        
        nombre_carta = input("📝 Ingresa el nombre de la carta: ").strip()
        if not nombre_carta:
            return
        
        # CONDICIONES DEL USUARIO - MÁS ESTRICTAS
        condiciones = {
            "precio_maximo": 1000,
        }
        
        print(f"\n🎯 Buscando: {nombre_carta}")
        print("   ✅ Filtros: Vendedores UE (sin UK) + Cartas Inglés + SOLO NM + Zero")
        
        inicio = time.time()
        
        # PASO 1: Buscar desde página principal
        print(f"\n🔍 PASO 1: Búsqueda desde página principal...")
        if not automator.buscar_desde_pagina_principal(nombre_carta):
            print("❌ Falló la búsqueda desde página principal")
            automator.mantener_abierto()
            return
        
        # PASO 2: Seleccionar carta más barata
        print(f"\n🔍 PASO 2: Seleccionando carta más barata...")
        if not automator.seleccionar_carta_mas_barata(nombre_carta):
            print("❌ No se pudo seleccionar la carta")
            automator.mantener_abierto()
            return
        
        tiempo_busqueda = time.time() - inicio
        print(f"⏱️  Tiempo de búsqueda: {tiempo_busqueda:.1f}s")
        
        # PASO 3: Buscar vendedores con filtros ESTRICTOS
        print(f"\n🔍 PASO 3: Buscando vendedores UE (sin UK) con cartas NM en inglés...")
        vendedores = automator.buscar_vendedores_con_zero_real(condiciones)
        
        if vendedores:
            print(f"\n🎯 MEJOR OPCIÓN ENCONTRADA:")
            mejor_vendedor = vendedores[0]
            paises = ', '.join(mejor_vendedor['paises']) if mejor_vendedor['paises'] else 'No especificado'
            
            print(f"   📦 Vendedor: {mejor_vendedor['vendedor']}")
            print(f"   💰 Precio: €{mejor_vendedor['precio']:.2f}")
            print(f"   🏷️  Condición: {mejor_vendedor['condicion']}")
            print(f"   📍 Ubicación: {paises}")
            print(f"   🗣️  Idioma: {mejor_vendedor['idioma']}")
            print(f"   🚚 Zero: ✅ Disponible")
            
            print(f"\n🛒 Agregando al carrito: {mejor_vendedor['vendedor']} - €{mejor_vendedor['precio']:.2f}")
            
            success = automator.agregar_al_carrito_confiable(mejor_vendedor)
            
            if success:
                print("🎉 ¡AUTOMATIZACIÓN COMPLETADA CON ÉXITO!")
                print("   Verifica tu carrito en el navegador")
            else:
                print("❌ No se pudo agregar al carrito")
                print("   Revisa el screenshot 'debug_carrito.png'")
        else:
            print("😞 No hay vendedores que cumplan TODOS los filtros:")
            print("   ✅ Zero disponible")
            print("   ✅ Ubicación en UE (sin UK)")
            print("   ✅ Carta en inglés") 
            print("   ✅ Condición NM (Near Mint)")
            print("   ✅ Precio dentro del rango")
            print("\n💡 Prueba con:")
            print("   - Aumentar el precio máximo")
            print("   - Buscar una carta diferente")
        
        tiempo_total = time.time() - inicio
        print(f"\n⏱️  TIEMPO TOTAL: {tiempo_total:.1f}s")
        
        automator.mantener_abierto()
        
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        automator.mantener_abierto()

if __name__ == "__main__":
    main()