from shared.base_automation import BaseAutomation
from cardtrader.cardtrader_selector import CardTraderSelector
from cardtrader.cardtrader_finder import CardTraderFinder
from utils import Utils
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

class CardTraderAutomation(BaseAutomation):
    def __init__(self):
        super().__init__("cardtrader")
        self.utils = Utils(self.driver)
        self.selector = CardTraderSelector(self.driver, self.utils)
        self.finder = CardTraderFinder(self.driver, self.utils)
    
    def buscar_desde_pagina_principal(self, nombre_carta):
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
        """Selecciona la carta más barata"""
        return self.selector.seleccionar_carta_mas_barata(nombre_carta)
    
    def buscar_vendedores_con_zero_real(self, condiciones, cantidad_necesaria=1):
        """Busca vendedores con Zero real"""
        return self.finder.buscar_vendedores_con_zero_real(condiciones, cantidad_necesaria)
    
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
            
            # Seleccionar n-ésima carta más barata
            carta_seleccionada = self.selector.seleccionar_nesima_carta_mas_barata(nombre_carta, intento)
            
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
            if vendedor.get('tiene_selector_cantidad', False) and copias_a_comprar > 1:
                if not self.finder.seleccionar_cantidad_en_selector(vendedor['selector_cantidad'], copias_a_comprar):
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