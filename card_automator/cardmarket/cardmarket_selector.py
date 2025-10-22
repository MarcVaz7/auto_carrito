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
    
    def _coincide_nombre_simplificado(self, nombre_buscado, nombre_encontrado):
        """Compara si los nombres simplificados coinciden exactamente"""
        buscado_simplificado = self._simplificar_nombre(nombre_buscado).lower()
        encontrado_simplificado = self._simplificar_nombre(nombre_encontrado).lower()
        
        print(f"     🔍 Comparando: '{buscado_simplificado}' vs '{encontrado_simplificado}'")
        return buscado_simplificado == encontrado_simplificado
    
    def _tiene_numero_correcto(self, contenedor):
        """Verifica que la carta tenga un número normal (no alternativo)"""
        try:
            # Buscar el elemento que contiene el número
            numero_element = contenedor.find_element(By.CSS_SELECTOR, ".col-number span:last-child")
            numero_texto = numero_element.text.strip()
            
            # Verificar que sea un número puro (sin letras)
            if numero_texto and numero_texto.isdigit():
                print(f"     ✅ Número válido: #{numero_texto}")
                return True
            else:
                print(f"     ❌ Número inválido: '{numero_texto}'")
                return False
                
        except Exception as e:
            print(f"     ❌ No se pudo encontrar número: {e}")
            return False
    
    def _obtener_enlace_carta(self, contenedor):
        """Obtiene el enlace a la página de la carta - CORREGIDO"""
        try:
            # PRIMER INTENTO: Buscar el enlace dentro del contenedor principal
            enlace = contenedor.find_element(By.CSS_SELECTOR, "a[href*='/Singles/']")
            url_carta = enlace.get_attribute('href')
            print(f"     ✅ Enlace encontrado: {url_carta}")
            return url_carta
        except:
            try:
                # SEGUNDO INTENTO: Buscar cualquier enlace que contenga el nombre
                enlaces = contenedor.find_elements(By.TAG_NAME, "a")
                for enlace in enlaces:
                    href = enlace.get_attribute('href')
                    if href and '/Singles/' in href:
                        print(f"     ✅ Enlace encontrado (alternativo): {href}")
                        return href
            except:
                pass
        
        print("     ❌ No se pudo encontrar el enlace")
        return None
    
    def seleccionar_carta_mas_barata(self, nombre_carta):
        """Selecciona la carta más barata en CardMarket que cumpla con los filtros"""
        try:
            print(f"🎯 CardMarket: Buscando '{nombre_carta}'...")
            
            # Esperar a que carguen los resultados
            time.sleep(3)
            
            # Buscar por el ID que contiene "productRow"
            contenedores_cartas = self.driver.find_elements(By.CSS_SELECTOR, "[id^='productRow']")
            print(f"📦 Encontrados {len(contenedores_cartas)} contenedores de cartas")
            
            cartas_encontradas = []
            
            for i, contenedor in enumerate(contenedores_cartas):
                try:
                    print(f"  🔍 Procesando carta {i+1}...")
                    
                    # FILTRO 1: Verificar que tenga número correcto
                    if not self._tiene_numero_correcto(contenedor):
                        continue
                    
                    # FILTRO 2: Extraer y comparar nombre
                    nombre_element = contenedor.find_element(By.CSS_SELECTOR, ".d-block.small.text-muted.fst-italic")
                    nombre_encontrado = nombre_element.text.strip()
                    print(f"     📝 Nombre encontrado: '{nombre_encontrado}'")
                    
                    # Verificar si coincide el nombre simplificado
                    if not self._coincide_nombre_simplificado(nombre_carta, nombre_encontrado):
                        print(f"     ❌ No coincide con '{nombre_carta}'")
                        continue
                    
                    print(f"     ✅ Coincide con '{nombre_carta}'")
                    
                    # FILTRO 3: Extraer precio
                    precio_element = contenedor.find_element(By.CSS_SELECTOR, ".col-price.pe-sm-2")
                    precio_texto = precio_element.text.strip()
                    print(f"     💰 Precio texto: '{precio_texto}'")
                    
                    # Limpiar y convertir precio
                    precio = self.utils.limpiar_y_convertir_precio_cardmarket(precio_texto)
                    
                    # CORRECCIÓN: Aceptar precios mayores a 0.01 en lugar de 0.10
                    if precio and precio >= 0.01:  # Cambiado de > 0.10 a >= 0.01
                        # Obtener el enlace usando el método corregido
                        url_carta = self._obtener_enlace_carta(contenedor)
                        
                        if url_carta:
                            cartas_encontradas.append({
                                'nombre': nombre_encontrado,
                                'precio': precio,
                                'url': url_carta,
                                'elemento': contenedor
                            })
                            print(f"     ✅ Añadida a la lista - Precio: €{precio:.2f}")
                        else:
                            print(f"     ❌ No se pudo obtener el enlace")
                    else:
                        print(f"     ❌ Precio no válido: {precio}")
                        
                except Exception as e:
                    print(f"     ⚠️ Error procesando carta {i+1}: {e}")
                    continue
            
            if not cartas_encontradas:
                print(f"❌ No se encontraron cartas que coincidan con '{nombre_carta}' y cumplan los filtros")
                return False
            
            # Ordenar por precio y seleccionar la más barata
            cartas_encontradas.sort(key=lambda x: x['precio'])
            carta_seleccionada = cartas_encontradas[0]
            
            print(f"✅ Carta seleccionada: {carta_seleccionada['nombre']}")
            print(f"💰 Precio: €{carta_seleccionada['precio']:.2f}")
            
            # Navegar a la página de la carta seleccionada
            print(f"🌐 Navegando a: {carta_seleccionada['url']}")
            self.driver.get(carta_seleccionada['url'])
            time.sleep(4)
            
            return True
            
        except Exception as e:
            print(f"❌ Error seleccionando carta en CardMarket: {e}")
            return False