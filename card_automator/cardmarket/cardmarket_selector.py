import time
import re
from selenium.webdriver.common.by import By

class CardMarketSelector:
    def __init__(self, driver, utils):
        self.driver = driver
        self.utils = utils
    
    def _simplificar_nombre(self, nombre):
        """Simplifica el nombre de la carta eliminando comas y caracteres especiales"""
        if not nombre:
            return ""
        
        # Eliminar comas y apóstrofes, mantener solo letras, números y espacios
        nombre_simplificado = re.sub(r"[,']", "", nombre)
        nombre_simplificado = re.sub(r"[^\w\s]", " ", nombre_simplificado)
        nombre_simplificado = re.sub(r"\s+", " ", nombre_simplificado).strip()
        
        return nombre_simplificado
    
    def _coincide_nombre_exacto(self, nombre_buscado, nombre_encontrado):
        """Compara si los nombres simplificados coinciden exactamente (case insensitive)"""
        buscado_simplificado = self._simplificar_nombre(nombre_buscado).lower()
        encontrado_simplificado = self._simplificar_nombre(nombre_encontrado).lower()
        
        print(f"     🔍 Comparando: '{buscado_simplificado}' vs '{encontrado_simplificado}'")
        return buscado_simplificado == encontrado_simplificado
    
    def seleccionar_carta_mas_barata(self, nombre_carta):
        """Selecciona la carta más barata - SOLO FILTRO POR NOMBRE EXACTO"""
        try:
            print(f"🎯 CardMarket: Buscando '{nombre_carta}'...")
            
            # Esperar a que carguen los resultados
            time.sleep(3)
            
            # Buscar todos los contenedores de cartas
            contenedores_cartas = self.driver.find_elements(By.CSS_SELECTOR, "[id^='productRow']")
            print(f"📦 Encontrados {len(contenedores_cartas)} contenedores de cartas")
            
            cartas_encontradas = []
            
            for i, contenedor in enumerate(contenedores_cartas):
                try:
                    print(f"  🔍 Procesando carta {i+1}...")
                    
                    # FILTRO 1: Nombre exacto (case insensitive)
                    nombre_element = contenedor.find_element(By.CSS_SELECTOR, ".d-block.small.text-muted.fst-italic")
                    nombre_encontrado = nombre_element.text.strip()
                    print(f"     📝 Nombre encontrado: '{nombre_encontrado}'")
                    
                    # Verificar si coincide el nombre exacto
                    if not self._coincide_nombre_exacto(nombre_carta, nombre_encontrado):
                        print(f"     ❌ No coincide exactamente con '{nombre_carta}'")
                        continue
                    
                    print(f"     ✅ Coincide exactamente con '{nombre_carta}'")
                    
                    # Extraer precio
                    precio_element = contenedor.find_element(By.CSS_SELECTOR, ".col-price.pe-sm-2")
                    precio_texto = precio_element.text.strip()
                    print(f"     💰 Precio: '{precio_texto}'")
                    
                    # Convertir precio
                    precio = self.utils.limpiar_y_convertir_precio_cardmarket(precio_texto)
                    
                    if precio and precio >= 0.01:
                        # Obtener enlace
                        enlace = contenedor.find_element(By.CSS_SELECTOR, "a[href*='/Singles/']")
                        url_carta = enlace.get_attribute('href')
                        
                        cartas_encontradas.append({
                            'nombre': nombre_encontrado,
                            'precio': precio,
                            'url': url_carta
                        })
                        print(f"     ✅ Añadida - €{precio:.2f}")
                    else:
                        print(f"     ❌ Precio inválido")
                        
                except Exception as e:
                    print(f"     ⚠️ Error procesando carta {i+1}: {e}")
                    continue
            
            if not cartas_encontradas:
                print(f"❌ No se encontraron cartas para '{nombre_carta}'")
                return False
            
            # Seleccionar la más barata
            cartas_encontradas.sort(key=lambda x: x['precio'])
            carta_seleccionada = cartas_encontradas[0]
            
            print(f"✅ Seleccionada: {carta_seleccionada['nombre']} - €{carta_seleccionada['precio']:.2f}")
            
            # Mostrar todas las opciones
            if len(cartas_encontradas) > 1:
                print(f"📊 Opciones encontradas ({len(cartas_encontradas)}):")
                for i, carta in enumerate(cartas_encontradas):
                    print(f"   {i+1}. {carta['nombre']} - €{carta['precio']:.2f}")
            
            # Navegar a la carta
            print(f"🌐 Navegando a: {carta_seleccionada['url']}")
            self.driver.get(carta_seleccionada['url'])
            time.sleep(4)
            
            return True
            
        except Exception as e:
            print(f"❌ Error seleccionando carta: {e}")
            return False