from shared.base_automation import BaseAutomation
from cardmarket.cardmarket_selector import CardMarketSelector
from cardmarket.cardmarket_finder import CardMarketFinder
from utils import Utils
import time

class CardMarketAutomation(BaseAutomation):
    def __init__(self):
        super().__init__("cardmarket")
        self.utils = Utils(self.driver)
        self.selector = CardMarketSelector(self.driver, self.utils)
        self.finder = CardMarketFinder(self.driver, self.utils)
    
    def buscar_desde_pagina_principal(self, nombre_carta):
        """Busca la carta en CardMarket usando la URL específica"""
        print(f"🔍 CardMarket: Iniciando búsqueda...")
        
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