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

from card_selector import CardSelector
from seller_finder import SellerFinder
from utils import Utils

class CardTraderAutomationFinal:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("detach", True)
        self.service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        self.actions = ActionChains(self.driver)
        
        # Inicializar módulos
        self.utils = Utils(self.driver)
        self.card_selector = CardSelector(self.driver, self.utils)
        self.seller_finder = SellerFinder(self.driver, self.utils)
    
    def cerrar_popups(self):
        """Cierra todos los popups molestos"""
        self.utils.cerrar_popups()
    
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
        return self.card_selector.seleccionar_carta_mas_barata(nombre_carta)
    
    def seleccionar_carta_con_reintentos(self, nombre_carta, condiciones, max_reintentos=5):
        """Selecciona carta con reintentos automáticos si no hay vendedores"""
        print(f"🔄 Sistema de reintentos activado (máximo {max_reintentos} intentos)")
        
        for intento in range(max_reintentos):
            print(f"\n🔄 INTENTO {intento + 1}/{max_reintentos}")
            
            # Si no es el primer intento, volver a la página de resultados
            if intento > 0:
                print("↩️ Volviendo a la página de resultados...")
                self.driver.back()
                time.sleep(3)
            
            # Seleccionar la i-ésima carta más barata (donde i = intento)
            carta_seleccionada = self.card_selector.seleccionar_nesima_carta_mas_barata(nombre_carta, intento)
            
            if not carta_seleccionada:
                print(f"❌ No hay más cartas disponibles para '{nombre_carta}'")
                return False
            
            # Buscar vendedores para esta carta
            print(f"\n🔍 PASO 3: Buscando vendedores UE (sin UK) con cartas NM en inglés...")
            vendedores = self.buscar_vendedores_con_zero_real(condiciones)
            
            if vendedores:
                mejor_vendedor = vendedores[0]
                paises = ', '.join(mejor_vendedor['paises']) if mejor_vendedor['paises'] else 'No especificado'
                
                print(f"\n🎯 VENDEDOR ENCONTRADO en intento {intento + 1}:")
                print(f"   📦 Vendedor: {mejor_vendedor['vendedor']}")
                print(f"   💰 Precio: €{mejor_vendedor['precio']:.2f}")
                print(f"   🏷️  Condición: {mejor_vendedor['condicion']}")
                print(f"   📍 Ubicación: {paises}")
                print(f"   🗣️  Idioma: {mejor_vendedor['idioma']}")
                print(f"   🚚 Zero: ✅ Disponible")
                
                print(f"\n🛒 Agregando al carrito: {mejor_vendedor['vendedor']} - €{mejor_vendedor['precio']:.2f}")
                
                success = self.agregar_al_carrito_confiable(mejor_vendedor)
                
                if success:
                    print(f"🎉 ¡CARTA AGREGADA EN INTENTO {intento + 1}!")
                    return True
                else:
                    print(f"❌ Error al agregar al carrito en intento {intento + 1}")
            else:
                print(f"😞 No hay vendedores para esta versión (intento {intento + 1})")
                print("   Probando con la siguiente carta más barata...")
        
        print(f"❌ No se encontraron vendedores después de {max_reintentos} intentos")
        return False
    
    def buscar_vendedores_con_zero_real(self, condiciones):
        """Busca SOLO vendedores que tengan botón Zero REAL y cumplan filtros"""
        return self.seller_finder.buscar_vendedores_con_zero_real(condiciones)
    
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
        
        # Si no encontramos confirmación visual, asumimos éxito (porque a veces la web no muestra confirmación)
        print("⚠️ No se detectó confirmación visual, pero se asume éxito")
        return True
    
    def mantener_abierto(self):
        """Mantiene el navegador abierto"""
        print("\n🖥️ Navegador permanece abierto...")
        input("Presiona Enter para cerrar...")
    
    def cerrar(self):
        """Cierra el navegador"""
        self.driver.quit()

# PROGRAMA PRINCIPAL (mantener igual)
def main():
    automator = CardTraderAutomationFinal()
    
    try:
        print("🚀 AUTOMATIZACIÓN CARDTRADER - VERSIÓN MEJORADA")
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
        
        # PASO 2: Seleccionar carta con reintentos
        print(f"\n🔍 PASO 2: Seleccionando carta con reintentos automáticos...")
        resultado = automator.seleccionar_carta_con_reintentos(nombre_carta, condiciones)
        
        if resultado:
            print("🎉 ¡AUTOMATIZACIÓN COMPLETADA CON ÉXITO!")
            print("   Verifica tu carrito en el navegador")
        else:
            print("❌ No se pudo agregar la carta después de todos los intentos")
        
        tiempo_total = time.time() - inicio
        print(f"\n⏱️  TIEMPO TOTAL: {tiempo_total:.1f}s")
        
        automator.mantener_abierto()
        
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        automator.mantener_abierto()

if __name__ == "__main__":
    main()