from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time
import re

class CardTraderDefinitivo:
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
                            print(f"✅ Popup cerrado: {selector}")
                            time.sleep(1)
                except:
                    continue
                    
            # JavaScript adicional para asegurar
            self.driver.execute_script("""
                var closeButtons = document.querySelectorAll('.iubenda-cs-close-btn, [iubenda-cc-close]');
                closeButtons.forEach(function(btn) { if(btn) btn.click(); });
            """)
        except Exception as e:
            print(f"ℹ️ No se pudieron cerrar popups: {e}")
    
    def buscar_vendedores_con_zero_real(self, url_carta, condiciones):
        """Busca SOLO vendedores que tengan botón Zero REAL (no celdas vacías)"""
        print(f"🔍 Analizando: {url_carta}")
        
        self.driver.get(url_carta)
        time.sleep(5)
        self.cerrar_popups()
        
        try:
            # Buscar TODAS las celdas Zero
            celdas_zero = self.driver.find_elements(By.CSS_SELECTOR, ".products-table__zero")
            print(f"📦 Celdas Zero encontradas: {len(celdas_zero)}")
            
            vendedores_con_zero_real = []
            
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
                            vendedores_con_zero_real.append(info)
                            print(f"  ✅ Vendedor {i+1}: {info['vendedor']} - €{info['precio']} - Zero REAL")
                    else:
                        vendedor_texto = fila.text.split('\n')[0] if fila.text else "Desconocido"
                        print(f"  ❌ Vendedor {i+1}: {vendedor_texto} - Zero VACÍO (sin stock)")
                        
                except Exception as e:
                    continue
            
            print(f"🎯 Vendedores con Zero REAL: {len(vendedores_con_zero_real)}")
            
            # Aplicar filtros
            vendedores_filtrados = self._aplicar_filtros_avanzados(vendedores_con_zero_real, condiciones)
            vendedores_filtrados.sort(key=lambda x: x['precio'])
            
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
            
            # Extraer condición
            try:
                condicion_elem = fila.find_element(By.CSS_SELECTOR, ".products-table__info--condition")
                info['condicion'] = condicion_elem.text
            except:
                info['condicion'] = "Desconocida"
            
            # Extraer ubicación
            try:
                banderas = fila.find_elements(By.CSS_SELECTOR, ".flag-icon")
                info['banderas'] = [bandera.get_attribute('class') for bandera in banderas]
                info['paises'] = self._clases_a_paises(info['banderas'])
            except:
                info['banderas'] = []
                info['paises'] = []
            
            info['fila'] = fila
            return info
            
        except Exception as e:
            print(f"⚠️ Error extrayendo info: {e}")
            return None
    
    def _clases_a_paises(self, clases_banderas):
        """Convierte clases de banderas a nombres de países"""
        mapeo = {
            'flag-icon-es': 'España',
            'flag-icon-fr': 'Francia', 
            'flag-icon-de': 'Alemania',
            'flag-icon-it': 'Italia',
            'flag-icon-gb': 'Reino Unido',
            'flag-icon-us': 'Estados Unidos',
            'flag-icon-ca': 'Canada',
            'flag-icon-pt': 'Portugal',
            'flag-icon-nl': 'Países Bajos'
        }
        
        paises = []
        for clase in clases_banderas:
            for clave, valor in mapeo.items():
                if clave in clase:
                    paises.append(valor)
        return list(set(paises))  # Remover duplicados
    
    def _aplicar_filtros_avanzados(self, vendedores, condiciones):
        """Aplica filtros avanzados"""
        vendedores_filtrados = []
        
        for vendedor in vendedores:
            cumple_condiciones = True
            
            # Filtro de precio máximo
            if vendedor['precio'] > condiciones.get('precio_maximo', 1000):
                cumple_condiciones = False
                continue
            
            # Filtro de ubicación UE
            if condiciones.get('solo_ue', False):
                paises_ue = ['España', 'Francia', 'Alemania', 'Italia', 'Portugal', 'Países Bajos']
                if not any(pais in vendedor['paises'] for pais in paises_ue):
                    cumple_condiciones = False
                    continue
            
            # Filtro de condición
            condiciones_aceptadas = condiciones.get('condiciones_aceptadas', ['NM', 'SP', 'LP'])
            if vendedor['condicion'] not in condiciones_aceptadas:
                cumple_condiciones = False
                continue
            
            if cumple_condiciones:
                vendedores_filtrados.append(vendedor)
        
        return vendedores_filtrados
    
    def agregar_al_carrito_confiable(self, vendedor):
        """Agrega al carrito de forma confiable"""
        print(f"🎯 Intentando agregar: {vendedor['vendedor']} - €{vendedor['precio']}")
        
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

# PROGRAMA PRINCIPAL
def main():
    automator = CardTraderDefinitivo()
    
    try:
        # CONDICIONES DEL USUARIO
        condiciones = {
            "precio_maximo": 60.00,
            "solo_ue": True,
            "condiciones_aceptadas": ["NM", "SP"]
        }
        
        url_carta = "https://www.cardtrader.com/cards/demonic-tutor-commander-masters"
        
        print("🚀 AUTOMATIZACIÓN DEFINITIVA - SOLO VENDEDORES CON ZERO REAL")
        print("=" * 60)
        
        # Buscar SOLO vendedores con Zero real (no celdas vacías)
        vendedores = automator.buscar_vendedores_con_zero_real(url_carta, condiciones)
        
        if vendedores:
            print(f"\n📊 VENDEDORES CON ZERO DISPONIBLE:")
            for i, vendedor in enumerate(vendedores, 1):
                paises = ', '.join(vendedor['paises']) if vendedor['paises'] else 'No especificado'
                print(f"  {i}. {vendedor['vendedor']} - €{vendedor['precio']:.2f} - {vendedor['condicion']} - {paises}")
            
            # Agregar el más barato automáticamente
            mejor_vendedor = vendedores[0]
            print(f"\n🛒 Agregando al carrito: {mejor_vendedor['vendedor']} - €{mejor_vendedor['precio']:.2f}")
            
            success = automator.agregar_al_carrito_confiable(mejor_vendedor)
            
            if success:
                print("🎉 ¡AUTOMATIZACIÓN COMPLETADA CON ÉXITO!")
                print("   Verifica tu carrito en el navegador")
            else:
                print("❌ No se pudo agregar al carrito")
                print("   Revisa el screenshot 'debug_carrito.png'")
        else:
            print("😞 No hay vendedores con Zero disponible que cumplan las condiciones")
            print("💡 Prueba con:")
            print("   - Aumentar el precio máximo")
            print("   - Quitar filtro UE")
            print("   - Aceptar más condiciones de carta")
        
        automator.mantener_abierto()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        automator.mantener_abierto()

if __name__ == "__main__":
    main()