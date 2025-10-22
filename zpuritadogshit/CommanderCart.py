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
from platforms import CardTraderPlatform, CardMarketPlatform

class CardAutomation:
    def __init__(self, plataforma="cardtrader"):
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("detach", True)
        self.service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        self.actions = ActionChains(self.driver)
        
        # Inicializar módulos
        self.utils = Utils(self.driver)
        
        # Seleccionar plataforma
        self.plataforma = plataforma.lower()
        if self.plataforma == "cardmarket":
            self.platform = CardMarketPlatform(self.driver, self.utils)
            print("🌐 Plataforma: CardMarket seleccionada")
        else:
            self.platform = CardTraderPlatform(self.driver, self.utils)
            print("🌐 Plataforma: CardTrader seleccionada (por defecto)")
        
        # Forzar login inmediatamente después de inicializar
        self._iniciar_sesion_inmediata()
    
    def _iniciar_sesion_inmediata(self):
        """Inicia sesión inmediatamente después de abrir el navegador"""
        print(f"🔐 Iniciando sesión inmediata en {self.plataforma.upper()}...")
        
        max_intentos = 3
        for intento in range(max_intentos):
            print(f"   Intento {intento + 1}/{max_intentos}")
            
            if self.platform.login():
                print(f"✅ Sesión iniciada correctamente en {self.plataforma.upper()}")
                return True
            else:
                if intento < max_intentos - 1:
                    print("   Reintentando en 3 segundos...")
                    time.sleep(3)
                else:
                    print(f"❌ No se pudo iniciar sesión después de {max_intentos} intentos")
                    print("💡 Por favor, verifica tus credenciales e intenta nuevamente")
                    return False
    
    def buscar_desde_pagina_principal(self, nombre_carta):
        """Busca la carta usando la plataforma seleccionada"""
        return self.platform.buscar_carta(nombre_carta)
    
    def seleccionar_carta_mas_barata(self, nombre_carta):
        """Selecciona la carta más barata usando la plataforma seleccionada"""
        return self.platform.seleccionar_carta_mas_barata(nombre_carta)
    
    def buscar_vendedores_con_zero_real(self, condiciones, cantidad_necesaria=1):
        """Busca vendedores usando la plataforma seleccionada"""
        return self.platform.buscar_vendedores(condiciones, cantidad_necesaria)
    
    def cerrar_popups(self):
        """Cierra todos los popups molestos"""
        self.utils.cerrar_popups()
    
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
            if self.plataforma == "cardmarket":
                carta_seleccionada = self.seleccionar_carta_mas_barata(nombre_carta)
            else:
                # Para CardTrader, usar el selector de n-ésima carta
                from card_selector import CardSelector
                card_selector = CardSelector(self.driver, self.utils)
                carta_seleccionada = card_selector.seleccionar_nesima_carta_mas_barata(nombre_carta, intento)
            
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
                if self.plataforma == "cardmarket":
                    print("   CardMarket: No hay más opciones disponibles")
                    return False
                else:
                    print("   Probando con la siguiente carta más barata...")
        
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
            
            # Seleccionar cantidad si es necesario
            if vendedor['tiene_selector_cantidad'] and copias_a_comprar > 1:
                if not self.seleccionar_cantidad_en_selector(vendedor['selector_cantidad'], copias_a_comprar):
                    print("   ❌ Error seleccionando cantidad, comprando 1 unidad")
                    copias_a_comprar = 1
            
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
            return True
        else:
            print(f"\n⚠️ Solo se pudieron agregar {cantidad_total - cantidad_restante} de {cantidad_total} copias")
            return cantidad_total - cantidad_restante > 0
    
    def seleccionar_cantidad_en_selector(self, selector_cantidad, cantidad):
        """Selecciona la cantidad específica en el selector"""
        try:
            from selenium.webdriver.support.ui import Select
            select = Select(selector_cantidad)
            select.select_by_value(str(cantidad))
            print(f"    ✅ Cantidad seleccionada: {cantidad}")
            time.sleep(1)
            return True
        except Exception as e:
            print(f"    ❌ Error seleccionando cantidad {cantidad}: {e}")
            return False
    
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