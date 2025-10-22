import time
import re
from selenium.webdriver.common.by import By

class CardMarketFinder:
    def __init__(self, driver, utils):
        self.driver = driver
        self.utils = utils
    
    def buscar_vendedores(self, condiciones, cantidad_necesaria=1):
        """Busca vendedores en CardMarket con los nuevos filtros - MODIFICADO para priorizar stock"""
        print("🔍 CardMarket: Buscando vendedores con filtros...")
        
        try:
            # Esperar a que cargue la página de vendedores
            time.sleep(3)
            
            vendedores = []
            
            # Buscar todos los contenedores de vendedores
            contenedores_vendedores = self.driver.find_elements(By.CSS_SELECTOR, "[id^='articleRow']")
            print(f"📦 Encontrados {len(contenedores_vendedores)} contenedores de vendedores")
            
            for i, contenedor in enumerate(contenedores_vendedores):
                try:
                    print(f"  🔍 Procesando vendedor {i+1}...")
                    
                    # Extraer información del vendedor
                    info_vendedor = self._extraer_info_vendedor(contenedor)
                    
                    if not info_vendedor:
                        continue
                    
                    # APLICAR FILTROS
                    if not self._cumple_filtros(info_vendedor, condiciones):
                        continue
                    
                    # Buscar el botón de agregar al carrito
                    boton_agregar = self._obtener_boton_agregar(contenedor)
                    
                    if boton_agregar:
                        vendedores.append({
                            'vendedor': info_vendedor['nombre'],
                            'precio': info_vendedor['precio'],
                            'stock_disponible': info_vendedor['stock_disponible'],
                            'reputacion': info_vendedor['reputacion'],
                            'condicion': info_vendedor['condicion'],
                            'idioma': info_vendedor['idioma'],
                            'tiene_selector_cantidad': False,
                            'elemento_click_zero': boton_agregar,
                            'info_completa': info_vendedor
                        })
                        print(f"     ✅ Vendedor cumple filtros: {info_vendedor['nombre']} - €{info_vendedor['precio']:.2f} - Stock: {info_vendedor['stock_disponible']}")
                    else:
                        print(f"     ❌ No se pudo encontrar botón de agregar para {info_vendedor['nombre']}")
                        
                except Exception as e:
                    print(f"     ⚠️ Error procesando vendedor {i+1}: {e}")
                    continue
            
            # MODIFICACIÓN CRÍTICA: Ordenar por stock disponible (mayor a menor) y luego por precio
            if vendedores:
                print("📊 Ordenando vendedores por stock disponible (mayor a menor)...")
                vendedores.sort(key=lambda x: (
                    -x['stock_disponible'],  # Primero por stock (mayor a menor)
                    x['precio']  # Luego por precio (menor a mayor)
                ))
                
                # Mostrar el top 5 de vendedores por stock
                print("🏆 TOP 5 VENDEDORES POR STOCK DISPONIBLE:")
                for i, vendedor in enumerate(vendedores[:5]):
                    print(f"   {i+1}. {vendedor['vendedor']} - Stock: {vendedor['stock_disponible']} - Precio: €{vendedor['precio']:.2f}")
            
            print(f"🎯 Vendedores que cumplen filtros: {len(vendedores)}")
            return vendedores
            
        except Exception as e:
            print(f"❌ Error buscando vendedores en CardMarket: {e}")
            return []

    def _extraer_info_vendedor(self, contenedor):
        """Extrae la información completa de un vendedor - Asegurar que esté correctamente indentado"""
        try:
            info = {}
            
            # 1. Extraer NOMBRE del vendedor
            try:
                nombre_element = contenedor.find_element(By.CSS_SELECTOR, ".seller-name a")
                info['nombre'] = nombre_element.text.strip()
                print(f"     👤 Vendedor: {info['nombre']}")
            except:
                print("     ❌ No se pudo extraer nombre del vendedor")
                return None
            
            # 2. Extraer PRECIO - SELECTOR CORREGIDO
            try:
                # Intentar diferentes selectores para el precio
                selectores_precio = [
                    ".color-primary.small.text-end.text-nowrap.fw-bold",
                    ".color-primary.fw-bold",
                    ".text-end .color-primary",
                    "[class*='price']",
                    ".fw-bold"
                ]
                
                precio_encontrado = False
                for selector in selectores_precio:
                    try:
                        elementos_precio = contenedor.find_elements(By.CSS_SELECTOR, selector)
                        for elemento in elementos_precio:
                            precio_texto = elemento.text.strip()
                            if precio_texto and '€' in precio_texto:
                                info['precio'] = self.utils.limpiar_y_convertir_precio_cardmarket(precio_texto)
                                if info['precio'] and info['precio'] > 0:
                                    print(f"     💰 Precio: €{info['precio']:.2f} (selector: {selector})")
                                    precio_encontrado = True
                                    break
                        if precio_encontrado:
                            break
                    except:
                        continue
                
                if not precio_encontrado:
                    print("     ❌ No se pudo extraer precio con ningún selector")
                    return None
                    
            except Exception as e:
                print(f"     ❌ Error extrayendo precio: {e}")
                return None
            
            # 3. Extraer REPUTACIÓN
            try:
                # Buscar diferentes tipos de reputación
                reputaciones = [
                    "fonticon-seller-rating-outstanding",  # Sobresaliente
                    "fonticon-seller-rating-excellent",    # Excelente
                    "fonticon-seller-rating-good",         # Bueno
                    "fonticon-seller-rating-neutral",      # Neutral
                    "fonticon-seller-rating-poor"          # Pobre
                ]
                
                info['reputacion'] = "Desconocida"
                for reputacion in reputaciones:
                    try:
                        elemento = contenedor.find_element(By.CSS_SELECTOR, f".{reputacion}")
                        if elemento:
                            if "outstanding" in reputacion:
                                info['reputacion'] = "Sobresaliente"
                            elif "excellent" in reputacion:
                                info['reputacion'] = "Excelente"
                            elif "good" in reputacion:
                                info['reputacion'] = "Bueno"
                            elif "neutral" in reputacion:
                                info['reputacion'] = "Neutral"
                            elif "poor" in reputacion:
                                info['reputacion'] = "Pobre"
                            break
                    except:
                        continue
                
                print(f"     ⭐ Reputación: {info['reputacion']}")
            except:
                info['reputacion'] = "Desconocida"
                print("     ⚠️ No se pudo determinar reputación")
            
            # 4. Extraer STOCK DISPONIBLE
            try:
                # Buscar el tooltip que contiene la información de stock
                stock_element = contenedor.find_element(By.CSS_SELECTOR, ".sell-count")
                tooltip_text = stock_element.get_attribute("data-bs-original-title")
                
                if tooltip_text:
                    # Extraer el número de artículos disponibles del tooltip
                    # Formato: "5005 Ventas | 48525 Artículos disponibles"
                    patron_stock = r'(\d+)\s*Artículos disponibles'
                    match = re.search(patron_stock, tooltip_text)
                    if match:
                        info['stock_disponible'] = int(match.group(1))
                    else:
                        info['stock_disponible'] = 1  # Por defecto
                else:
                    info['stock_disponible'] = 1
                
                print(f"     📊 Stock disponible: {info['stock_disponible']}")
            except:
                info['stock_disponible'] = 1
                print("     ⚠️ No se pudo determinar stock, usando 1 por defecto")
            
            # 5. Extraer CONDICIÓN de la carta
            try:
                condicion_element = contenedor.find_element(By.CSS_SELECTOR, ".article-condition .badge")
                info['condicion'] = condicion_element.text.strip()
                print(f"     🎯 Condición: {info['condicion']}")
            except:
                info['condicion'] = "Desconocida"
                print("     ⚠️ No se pudo determinar condición")
            
            # 6. Extraer IDIOMA de la carta
            try:
                # Buscar la bandera de idioma (Inglés)
                bandera_ingles = contenedor.find_element(By.CSS_SELECTOR, "[aria-label='Inglés']")
                info['idioma'] = "Inglés"
                print(f"     🏴󠁧󠁢󠁥󠁮󠁧󠁿 Idioma: {info['idioma']}")
            except:
                info['idioma'] = "Desconocido"
                print("     ⚠️ No se pudo determinar idioma")
            
            return info
            
        except Exception as e:
            print(f"     ❌ Error extrayendo información del vendedor: {e}")
            return None

    def _cumple_filtros(self, info_vendedor, condiciones):
        """Verifica si el vendedor cumple con todos los filtros"""
        
        # FILTRO 1: Condición mínima NM (Near Mint)
        condiciones_aceptadas = ['NM']  # Solo Near Mint
        if info_vendedor['condicion'] not in condiciones_aceptadas:
            print(f"     ❌ Condición no aceptada: {info_vendedor['condicion']}")
            return False
        
        # FILTRO 2: Idioma Inglés
        if info_vendedor['idioma'] != "Inglés":
            print(f"     ❌ Idioma no aceptado: {info_vendedor['idioma']}")
            return False
        
        # FILTRO 3: Reputación mínima (opcional, pero buena práctica)
        reputaciones_aceptadas = ['Sobresaliente', 'Excelente', 'Bueno']
        if info_vendedor['reputacion'] not in reputaciones_aceptadas:
            print(f"     ❌ Reputación no aceptada: {info_vendedor['reputacion']}")
            return False
        
        # FILTRO 4: Precio máximo (si se especifica)
        precio_maximo = condiciones.get('precio_maximo', 1000)
        if info_vendedor['precio'] > precio_maximo:
            print(f"     ❌ Precio excede máximo: €{info_vendedor['precio']:.2f} > €{precio_maximo:.2f}")
            return False
        
        # FILTRO 5: Stock suficiente
        cantidad_necesaria = condiciones.get('cantidad_necesaria', 1)
        if info_vendedor['stock_disponible'] < cantidad_necesaria:
            print(f"     ❌ Stock insuficiente: {info_vendedor['stock_disponible']} < {cantidad_necesaria}")
            return False
        
        print("     ✅ Vendedor cumple todos los filtros")
        return True

    def _obtener_boton_agregar(self, contenedor):
        """Obtiene el botón de agregar al carrito"""
        try:
            # Buscar el botón de formulario (versión desktop)
            try:
                boton = contenedor.find_element(By.CSS_SELECTOR, "button[type='submit']")
                if boton.is_displayed() and "btn-primary" in boton.get_attribute("class"):
                    print("     ✅ Botón de agregar encontrado (desktop)")
                    return boton
            except:
                pass
            
            # Buscar el botón móvil (fallback)
            try:
                boton = contenedor.find_element(By.CSS_SELECTOR, ".mobile-cart.btn-primary")
                if boton.is_displayed():
                    print("     ✅ Botón de agregar encontrado (móvil)")
                    return boton
            except:
                pass
            
            # Buscar cualquier botón con icono de carrito
            try:
                botones = contenedor.find_elements(By.CSS_SELECTOR, ".btn-primary")
                for boton in botones:
                    if "cart" in boton.get_attribute("innerHTML").lower():
                        print("     ✅ Botón de agregar encontrado (genérico)")
                        return boton
            except:
                pass
            
            print("     ❌ No se pudo encontrar botón de agregar")
            return None
            
        except Exception as e:
            print(f"     ❌ Error buscando botón: {e}")
            return None