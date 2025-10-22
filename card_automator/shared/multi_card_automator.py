from CommanderCart import CardAutomation
import time
from selenium.webdriver.common.keys import Keys
import re
from collections import Counter

class MultiCardAutomator:
    def __init__(self, plataforma="cardtrader"):
        self.plataforma = plataforma
        self.automator = CardAutomation(plataforma)
        self.condiciones = {
            "precio_maximo": 1000,
        }
        self.cartas_agregadas = []  # Cartas únicas que se añadieron exitosamente
        self.cartas_fallidas = []   # Cartas únicas que fallaron
        self.copias_agregadas = 0   # Contador total de copias añadidas
        self.copias_falladas = 0    # Contador total de copias falladas
    
    def procesar_linea_carta(self, linea):
        """
        Procesa una línea de texto que puede contener:
        - Número de copias (ej: "2 Mountain")
        - Nombre con coma (ej: "Sauron, The Dark Lord")
        
        Retorna: lista de nombres de cartas (puede tener múltiples copias)
        """
        if not linea.strip():
            return []
        
        linea = linea.strip()
        
        # Buscar número al inicio (ej: "2 Mountain", "3x Forest", "1 Sol Ring")
        patron_numero = r'^(\d+)\s*(?:x\s*)?(.+)$'
        match = re.match(patron_numero, linea)
        
        if match:
            cantidad = int(match.group(1))
            nombre_carta = match.group(2).strip()
            
            # Si la carta tiene coma en el nombre (ej: "Sauron, The Dark Lord"),
            # mantenerla como una sola carta reemplazando la coma por espacio
            if ',' in nombre_carta:
                nombre_carta = nombre_carta.replace(',', ' ')
            
            # Limpiar espacios múltiples
            nombre_carta = re.sub(r'\s+', ' ', nombre_carta).strip()
            
            # Capitalizar palabras (excepto palabras pequeñas)
            palabras = nombre_carta.split()
            palabras_capitalizadas = []
            
            for palabra in palabras:
                if len(palabra) > 2:  # Solo capitalizar palabras de 3+ letras
                    palabras_capitalizadas.append(palabra.capitalize())
                else:
                    palabras_capitalizadas.append(palabra.lower())
            
            nombre_carta = ' '.join(palabras_capitalizadas)
            
            # Retornar múltiples copias si la cantidad es > 1
            return [nombre_carta] * cantidad
        
        else:
            # No hay número, procesar como carta única
            nombre_carta = linea
            
            # Manejar comas en el nombre
            if ',' in nombre_carta:
                nombre_carta = nombre_carta.replace(',', ' ')
            
            # Limpiar espacios múltiples
            nombre_carta = re.sub(r'\s+', ' ', nombre_carta).strip()
            
            # Capitalizar palabras
            palabras = nombre_carta.split()
            palabras_capitalizadas = []
            
            for palabra in palabras:
                if len(palabra) > 2:
                    palabras_capitalizadas.append(palabra.capitalize())
                else:
                    palabras_capitalizadas.append(palabra.lower())
            
            nombre_carta = ' '.join(palabras_capitalizadas)
            
            return [nombre_carta]
    
    def limpiar_y_procesar_lista_cartas(self, lista_cartas):
        """
        Procesa la lista de cartas línea por línea, manejando cantidades y nombres con comas
        """
        todas_las_cartas = []
        
        for linea in lista_cartas:
            cartas_de_esta_linea = self.procesar_linea_carta(linea)
            todas_las_cartas.extend(cartas_de_esta_linea)
        
        return todas_las_cartas
    
    def procesar_lista_cartas(self, lista_cartas):
        """Procesa múltiples cartas cerrando pestañas anteriores"""
        # Primero procesar la lista completa manejando cantidades y comas
        lista_procesada_completa = self.limpiar_y_procesar_lista_cartas(lista_cartas)
        
        # Obtener cartas únicas con sus cantidades
        contador_cartas = Counter(lista_procesada_completa)
        cartas_unicas = list(contador_cartas.keys())
        
        print(f"\n🎯 Procesando {len(cartas_unicas)} cartas únicas ({len(lista_procesada_completa)} copias en total):")
        
        # Mostrar desglose
        print("📊 Desglose de cartas:")
        for carta, cantidad in sorted(contador_cartas.items()):
            if cantidad > 1:
                print(f"   - {carta} (x{cantidad})")
            else:
                print(f"   - {carta}")
        
        # Procesar cada carta única una sola vez
        for i, nombre_carta in enumerate(cartas_unicas, 1):
            cantidad_necesaria = contador_cartas[nombre_carta]
            
            print(f"\n{'='*60}")
            print(f"📑 CARTA {i}/{len(cartas_unicas)}: '{nombre_carta}' (x{cantidad_necesaria})")
            print(f"{'='*60}")
            
            resultado = self._procesar_carta_en_pestana(nombre_carta, cantidad_necesaria, i)
            
            if resultado:
                self.cartas_agregadas.append(nombre_carta)
                self.copias_agregadas += cantidad_necesaria
            else:
                self.cartas_fallidas.append(nombre_carta)
                self.copias_falladas += cantidad_necesaria
            
            # Cerrar pestaña actual y abrir nueva para la siguiente carta
            if i < len(cartas_unicas):
                self._cerrar_y_abrir_nueva_pestana()
        
        return len(self.cartas_agregadas), len(self.cartas_fallidas)
    
    def _cerrar_y_abrir_nueva_pestana(self):
        """Cierra la pestaña actual y abre una nueva"""
        try:
            # Guardar el handle de la pestaña actual
            current_handle = self.automator.driver.current_window_handle
            
            # Abrir nueva pestaña
            self.automator.driver.execute_script("window.open('');")
            
            # Obtener todos los handles
            all_handles = self.automator.driver.window_handles
            
            # Cambiar a la nueva pestaña (la última)
            new_handle = all_handles[-1]
            self.automator.driver.switch_to.window(new_handle)
            
            # Cerrar la pestaña anterior
            self.automator.driver.switch_to.window(current_handle)
            self.automator.driver.close()
            
            # Volver a la nueva pestaña
            self.automator.driver.switch_to.window(new_handle)
            
            time.sleep(1)
            
        except Exception as e:
            print(f"⚠️ Error al cambiar de pestaña: {e}")
            try:
                if len(self.automator.driver.window_handles) == 0:
                    self.automator.driver.execute_script("window.open('');")
                    self.automator.driver.switch_to.window(self.automator.driver.window_handles[-1])
                else:
                    self.automator.driver.switch_to.window(self.automator.driver.window_handles[-1])
            except:
                print("🔄 Reiniciando navegador...")
                self.automator.cerrar()
                self.automator = CardAutomation(self.plataforma)
    
    def _procesar_carta_en_pestana(self, nombre_carta, cantidad_necesaria, numero_carta):
        """Procesa una carta en la pestaña actual con reintentos automáticos"""
        try:
            inicio = time.time()
            
            # PASO 1: Buscar desde página principal
            if not self.automator.buscar_desde_pagina_principal(nombre_carta):
                return False
            
            # PASO 2: Seleccionar carta más barata (con reintentos automáticos si no hay vendedores)
            print(f"\n🔍 PASO 2: Seleccionando carta con reintentos automáticos...")
            print(f"📦 Cantidad necesaria: {cantidad_necesaria} copias")
            
            resultado = self.automator.seleccionar_carta_con_reintentos(
                nombre_carta, 
                self.condiciones, 
                cantidad_necesaria
            )
            
            if resultado:
                tiempo_total = time.time() - inicio
                print(f"✅ '{nombre_carta}' (x{cantidad_necesaria}) agregada correctamente")
                print(f"⏱️  TIEMPO TOTAL: {tiempo_total:.1f}s")
                return True
            else:
                print(f"❌ No se pudo agregar '{nombre_carta}' (x{cantidad_necesaria}) después de todos los intentos")
                return False
                
        except Exception as e:
            print(f"❌ Error procesando '{nombre_carta}': {e}")
            return False
    
    def mostrar_resumen(self):
        """Muestra un resumen detallado de los resultados"""
        print(f"\n{'='*60}")
        print("📊 RESUMEN FINAL")
        print(f"{'='*60}")
        
        print(f"✅ Se han añadido {len(self.cartas_agregadas)} cartas únicas")
        print(f"📦 Total de copias añadidas: {self.copias_agregadas}")
        
        if self.cartas_fallidas:
            print(f"❌ Han fallado {len(self.cartas_fallidas)} cartas únicas")
            print(f"📦 Total de copias falladas: {self.copias_falladas}")
            print(f"\n📋 Cartas que faltaron por añadir:")
            for carta in self.cartas_fallidas:
                print(f"   - {carta}")
        else:
            print("🎉 ¡Todas las cartas se añadieron correctamente!")
        
        # Mostrar cuántas pestañas quedan abiertas
        try:
            pestañas_abiertas = len(self.automator.driver.window_handles)
            print(f"\n📑 Pestañas abiertas: {pestañas_abiertas}")
        except:
            print("\n📑 Navegador cerrado")
    
    def cerrar_todo(self):
        """Cierra todas las pestañas y el navegador"""
        self.automator.cerrar()

    def mostrar_vendedores_seleccionados(self):
        """Muestra todos los vendedores seleccionados durante la sesión"""
        vendedores = self.automator.obtener_vendedores_seleccionados()
        
        if not vendedores:
            print("\n📋 No se han guardado vendedores en el arraylist")
            return
        
        print(f"\n{'='*60}")
        print("🏪 VENDEDORES SELECCIONADOS EN ESTA SESIÓN")
        print(f"{'='*60}")
        
        # Agrupar por vendedor
        from collections import defaultdict
        vendedores_agrupados = defaultdict(list)
        
        for vendedor in vendedores:
            vendedores_agrupados[vendedor['nombre']].append(vendedor)
        
        for nombre_vendedor, transacciones in vendedores_agrupados.items():
            total_copias = sum(t['copias_compradas'] for t in transacciones)
            total_gastado = sum(t['precio_unitario'] * t['copias_compradas'] for t in transacciones)
            cartas_compradas = set(t['carta'] for t in transacciones)
            
            print(f"\n🏷️  {nombre_vendedor}:")
            print(f"   📦 Total copias compradas: {total_copias}")
            print(f"   💰 Total gastado: €{total_gastado:.2f}")
            print(f"   🎴 Cartas compradas: {len(cartas_compradas)}")
            print(f"   📋 Cartas: {', '.join(sorted(cartas_compradas))}")