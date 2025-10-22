import time
import re
from selenium.webdriver.common.by import By

class CardTraderFinder:
    def __init__(self, driver, utils):
        self.driver = driver
        self.utils = utils
    
    def buscar_vendedores_con_zero_real(self, condiciones, cantidad_necesaria=1):
        """Busca SOLO vendedores que tengan botón Zero REAL y cumplan filtros de ubicación e idioma - MODIFICADO para priorizar stock"""
        print("🔍 Analizando vendedores en la página de la carta...")
        
        self.utils.cerrar_popups()
        
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
                        info = self._extraer_info_vendedor_completo(fila, celda_zero, cantidad_necesaria)
                        if info and info['precio'] > 0:
                            # Aplicar filtros de ubicación e idioma
                            if self._cumple_filtros_ubicacion_idioma(info):
                                vendedores_con_zero_real.append(info)
                    else:
                        continue
                        
                except Exception as e:
                    continue
            
            print(f"🎯 Vendedores que cumplen filtros UE (sin UK) + Inglés: {len(vendedores_con_zero_real)}")
        
            # Aplicar filtros adicionales (condición, precio máximo)
            vendedores_filtrados = self._aplicar_filtros_avanzados(vendedores_con_zero_real, condiciones)
            
            # MODIFICACIÓN: ORDENAR por stock disponible (MAYOR a menor) y luego por precio
            print("📊 Ordenando vendedores por stock disponible (mayor a menor)...")
            vendedores_filtrados.sort(key=lambda x: (
                -x.get('stock_disponible', 0),  # Primero por stock disponible (mayor a menor)
                x['precio']  # Luego por precio (menor a mayor)
            ))
            
            # Mostrar el top 5 de vendedores por stock
            if vendedores_filtrados:
                print("🏆 TOP 5 VENDEDORES POR STOCK DISPONIBLE:")
                for i, vendedor in enumerate(vendedores_filtrados[:5]):
                    stock_info = f"Stock: {vendedor.get('stock_disponible', 'N/A')}"
                    if vendedor.get('stock_suficiente'):
                        stock_info += " ✅"
                    else:
                        stock_info += " ⚠️"
                    print(f"   {i+1}. {vendedor['vendedor']} - {stock_info} - Precio: €{vendedor['precio']:.2f}")
            
            return vendedores_filtrados
            
        except Exception as e:
            print(f"❌ Error en búsqueda: {e}")
            return []
    
    def _extraer_info_vendedor_completo(self, fila, celda_zero, cantidad_necesaria):
        """Extrae información completa del vendedor con Zero real, incluyendo stock"""
        try:
            info = {}
            
            # Extraer nombre del vendedor
            try:
                vendedor_elem = fila.find_element(By.CSS_SELECTOR, ".products-table__seller")
                info['vendedor'] = vendedor_elem.text
            except:
                info['vendedor'] = "Desconocido"
            
            # Extraer precio
            info['precio'] = 0.0
            try:
                precio_elem = fila.find_element(By.CSS_SELECTOR, ".products-table__formatted-price")
                precio_texto = precio_elem.text
                
                # Buscar el patrón de precio en el texto
                patron_precio = r'€\s*([0-9]{1,3}(?:[.,][0-9]{3})*(?:[.,][0-9]{2})?)'
                match = re.search(patron_precio, precio_texto)
                
                if match:
                    precio_str = match.group(1)
                    info['precio'] = self.utils.limpiar_y_convertir_precio(precio_str)
                else:
                    print(f"    ⚠️ No se pudo extraer precio del texto: '{precio_texto}'")
                            
            except Exception as e:
                info['precio'] = 0.0
            
            # Extraer STOCK DISPONIBLE
            info['stock_disponible'] = 1  # Por defecto 1
            info['tiene_selector_cantidad'] = False
            
            try:
                # Buscar el selector de cantidad
                selector_cantidad = fila.find_element(By.CSS_SELECTOR, ".products-table__quantity-form select")
                info['tiene_selector_cantidad'] = True
                
                # Obtener todas las opciones disponibles
                opciones = selector_cantidad.find_elements(By.TAG_NAME, "option")
                if opciones:
                    # La última opción es el máximo disponible
                    max_stock = int(opciones[-1].get_attribute('value'))
                    info['stock_disponible'] = max_stock
                    print(f"    📦 Stock disponible: {max_stock} unidades")
                
                # Guardar el elemento del selector para usarlo después
                info['selector_cantidad'] = selector_cantidad
                
            except:
                # Si no hay selector, asumimos que solo tiene 1 unidad
                info['stock_disponible'] = 1
                info['tiene_selector_cantidad'] = False
                print(f"    📦 Stock disponible: 1 unidad (sin selector)")
            
            # Verificar si tiene stock suficiente
            info['stock_suficiente'] = info['stock_disponible'] >= cantidad_necesaria
            
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

    def _aplicar_filtros_avanzados(self, vendedores, condiciones):
        """Aplica filtros avanzados"""
        vendedores_filtrados = []
        
        for vendedor in vendedores:
            cumple_condiciones = True
            
            # Filtro de precio máximo
            if vendedor['precio'] > condiciones.get('precio_maximo', 1000):
                cumple_condiciones = False
                continue
            
            if cumple_condiciones:
                vendedores_filtrados.append(vendedor)
        
        return vendedores_filtrados

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