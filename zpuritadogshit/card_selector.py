import time
import re
import unicodedata
from selenium.webdriver.common.by import By

class CardSelector:
    def __init__(self, driver, utils):
        self.driver = driver
        self.utils = utils
    
    def seleccionar_carta_mas_barata(self, nombre_carta):
        """Selecciona la carta más barata de los resultados que cumple con el filtro de número"""
        return self.seleccionar_nesima_carta_mas_barata(nombre_carta, 0)
    
    def seleccionar_nesima_carta_mas_barata(self, nombre_carta, indice=0):
        """Selecciona la n-ésima carta más barata (0 = más barata, 1 = segunda más barata, etc.)"""
        try:
            # DETECTAR TIPO DE PÁGINA: ¿Estamos en página directa de vendedores o en selección de versiones?
            if self._es_pagina_directa_de_vendedores():
                return True
            
            cartas_encontradas = self._obtener_todas_las_cartas_validas(nombre_carta)
            
            if not cartas_encontradas:
                print("❌ No se encontraron cartas que coincidan y cumplan los filtros")
                return False
            
            # Verificar si el índice solicitado existe
            if indice >= len(cartas_encontradas):
                print(f"❌ No hay {indice + 1} cartas disponibles. Solo hay {len(cartas_encontradas)}")
                return False
            
            # Seleccionar la n-ésima carta más barata
            cartas_encontradas.sort(key=lambda x: x['precio'])
            carta_seleccionada = cartas_encontradas[indice]
            
            print(f"🎯 CARTA SELECCIONADA (opción #{indice + 1}):")
            print(f"   📦 {self._extraer_nombre_legible_del_href(carta_seleccionada['url'])}")
            print(f"   💰 €{carta_seleccionada['precio']:.2f}")
            if indice > 0:
                print(f"   🔄 Intentando opción alternativa #{indice + 1}")
            
            # Navegar a la carta seleccionada
            self.driver.get(carta_seleccionada['url'])
            time.sleep(4)
            
            # Después de navegar, verificar si necesitamos ir a la página de vendedores
            if not self._es_pagina_directa_de_vendedores():
                if not self._navegar_a_pagina_vendedores():
                    return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error en selección: {e}")
            return False
    
    def _obtener_todas_las_cartas_validas(self, nombre_carta):
        """Obtiene todas las cartas válidas ordenadas por precio"""
        cartas_encontradas = []
        
        # ESTRATEGIA: Buscar enlaces de cartas en los resultados
        enlaces_cartas = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/cards/']")
        
        for enlace in enlaces_cartas[:40]:
            try:
                texto = enlace.text.strip()
                if not texto or len(texto) < 3:
                    continue
                
                # Buscar el contenedor completo de la carta
                contenedor = self._encontrar_contenedor_carta(enlace)
                if contenedor:
                    carta = self._extraer_carta_desde_contenedor(contenedor, nombre_carta)
                    if carta and carta['precio'] > 0.10:
                        cartas_encontradas.append(carta)
            except:
                continue
        
        # Estrategia alternativa si no encontramos suficientes cartas
        if len(cartas_encontradas) < 3:
            cartas_alternativas = self._busqueda_alternativa_cartas(nombre_carta)
            for carta in cartas_alternativas:
                if carta not in cartas_encontradas:
                    cartas_encontradas.append(carta)
        
        # Ordenar por precio
        cartas_encontradas.sort(key=lambda x: x['precio'])
        
        print(f"📊 Se encontraron {len(cartas_encontradas)} cartas válidas:")
        for i, carta in enumerate(cartas_encontradas):
            nombre_legible = self._extraer_nombre_legible_del_href(carta['url'])
            print(f"   {i+1}. {nombre_legible[:35]}... - €{carta['precio']:.2f}")
        
        return cartas_encontradas
    
    def _es_pagina_directa_de_vendedores(self):
        """Detecta si estamos en una página directa de vendedores (sin selección de versiones)"""
        try:
            current_url = self.driver.current_url.lower()
            
            if '/cards/' in current_url:
                parametros_busqueda = ['?', 'search=', 'q=', 'query=']
                tiene_parametros_busqueda = any(param in current_url for param in parametros_busqueda)
                
                if not tiene_parametros_busqueda:
                    return True
            
            elementos_vendedores = [
                ".products-table",
                ".products-table__seller",
                ".products-table__zero",
                "//th[contains(text(), 'Seller')]",
                "//th[contains(text(), 'Vendedor')]",
            ]
            
            for elemento in elementos_vendedores:
                try:
                    if "//" in elemento:
                        elementos = self.driver.find_elements(By.XPATH, elemento)
                    else:
                        elementos = self.driver.find_elements(By.CSS_SELECTOR, elemento)
                    
                    if elementos and any(elem.is_displayed() for elem in elementos):
                        return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            return False
    
    def _navegar_a_pagina_vendedores(self):
        """Navega desde la página de detalles de la carta a la página de vendedores"""
        try:
            # Estrategia 1: Buscar pestaña "Sellers" o "Vendedores"
            selectores_pestanas = [
                "//a[contains(@href, 'sellers')]",
                "//a[contains(@href, 'prices')]",
                "//button[contains(text(), 'Sellers')]",
                "//button[contains(text(), 'Vendedores')]",
            ]
            
            for selector in selectores_pestanas:
                try:
                    if "//" in selector:
                        elementos = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elementos = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for elemento in elementos:
                        if elemento.is_displayed():
                            self.driver.execute_script("arguments[0].click();", elemento)
                            time.sleep(3)
                            return True
                except:
                    continue
            
            # Estrategia 2: Modificar la URL
            current_url = self.driver.current_url
            if '/cards/' in current_url and '/sellers' not in current_url:
                if '?' in current_url:
                    base_url = current_url.split('?')[0]
                else:
                    base_url = current_url
                
                sellers_url = base_url + '/sellers'
                self.driver.get(sellers_url)
                time.sleep(3)
                return True
            
            return False
            
        except Exception as e:
            return False
    
    def _encontrar_contenedor_carta(self, enlace):
        """Encuentra el contenedor completo de una carta - VERSIÓN MEJORADA"""
        try:
            # Buscar contenedores específicos de cartas en los resultados
            selectores_contenedor = [
                ".blueprint-search-card",
                ".blueprint-search__search-result-card", 
                "[class*='card']",
                ".product-item"
            ]
            
            for selector in selectores_contenedor:
                try:
                    contenedor = enlace.find_element(By.XPATH, f"./ancestor::div[contains(@class, '{selector.replace('.', '')}')]")
                    if contenedor and contenedor.is_displayed():
                        return contenedor
                except:
                    continue
            
            # Fallback: buscar contenedores cercanos
            for i in range(1, 4):
                try:
                    contenedor = enlace.find_element(By.XPATH, f"./ancestor::div[{i}]")
                    texto = contenedor.text.strip()
                    if texto and '€' in texto and len(texto) > 50 and len(texto) < 500:
                        return contenedor
                except:
                    continue
            return enlace
        except:
            return enlace
    
    def _extraer_carta_desde_contenedor(self, contenedor, nombre_carta):
        """Extrae información de carta desde un contenedor - VERSIÓN LIMPIA"""
        try:
            texto = contenedor.text.strip()
            if not texto or len(texto) < 20:
                return None
            
            carta = {}
            
            # ESTRATEGIA MEJORADA: Buscar el href completo para la comparación
            href_completo = self._extraer_nombre_ingles(contenedor)
            
            if href_completo:
                carta['nombre'] = href_completo
            else:
                # Fallback: usar el nombre en español del texto
                lineas = [l.strip() for l in texto.split('\n') if l.strip()]
                for linea in lineas:
                    if self.utils.coincidencia_flexible(linea, nombre_carta) and len(linea) > 5:
                        carta['nombre'] = linea
                        break
                
                if 'nombre' not in carta:
                    for linea in lineas:
                        if len(linea) > 5 and not any(x in linea for x in ['€', 'Añadir', 'Add']):
                            carta['nombre'] = linea
                            break
            
            if 'nombre' not in carta:
                return None
            
            # FILTRO MEJORADO: Verificar que el href CONTENGA el nombre buscado (ignorando símbolos)
            if href_completo and not self._coincidencia_exacta_ignorando_simbolos(href_completo, nombre_carta):
                return None
            
            if href_completo and any(palabra in href_completo.lower() for palabra in ["prophecy"]):
                return None
            
            # Si no encontramos href, usar coincidencia flexible con el nombre en español
            elif not href_completo and not self.utils.coincidencia_flexible(carta['nombre'], nombre_carta):
                return None
            
            # FILTRO NUEVO: Verificar que la carta tenga exactamente #numero y NO #Anumero
            tiene_numero_correcto = False
            tiene_numero_alternativo = False
            
            # Buscar patrones de número en el texto completo
            patron_numero_normal = re.search(r'#(\d+)', texto)
            patron_numero_alternativo = re.search(r'#A(\d+)', texto)
            
            # Solo aceptar si tiene #numero y NO tiene #Anumero
            if patron_numero_normal and not patron_numero_alternativo:
                tiene_numero_correcto = True
                carta['numero'] = patron_numero_normal.group(1)
            elif patron_numero_alternativo:
                tiene_numero_alternativo = True
                carta['numero_alternativo'] = patron_numero_alternativo.group(1)
            
            # Si no tiene el formato correcto de número, rechazar la carta
            if not tiene_numero_correcto:
                return None
            
            # NUEVO FILTRO: Rechazar cartas que contengan "Display Commander"
            if "display commander" in texto.lower():
                return None
            
            # SOLUCIÓN CRÍTICA: Extraer URL ANTES de extraer precios
            try:
                enlaces = contenedor.find_elements(By.TAG_NAME, "a")
                for enlace in enlaces:
                    href = enlace.get_attribute('href')
                    if href and '/cards/' in href:
                        carta['url'] = href
                        break
                if 'url' not in carta:
                    return None
            except:
                return None
            
            # Extraer precio
            carta['precio'] = self._extraer_precio_especifico_carta(contenedor, texto)
            
            if carta['precio'] and carta['precio'] > 0.10:
                return carta
            else:
                return None
            
        except Exception as e:
            return None

    def _extraer_precio_especifico_carta(self, contenedor, texto_completo):
        """Extrae SOLO el precio específico de la carta actual"""
        try:
            # ESTRATEGIA 1: Buscar el precio en el elemento de precio específico
            selectores_precio = [
                ".blueprint-search-card__price",
                "[class*='price']",
                ".text-success.font-weight-bold",
                "span.text-success"
            ]
            
            for selector in selectores_precio:
                try:
                    elementos_precio = contenedor.find_elements(By.CSS_SELECTOR, selector)
                    for elemento in elementos_precio:
                        texto_precio = elemento.text.strip()
                        if texto_precio and '€' in texto_precio:
                            patron_precio = r'€\s*([0-9]{1,3}(?:[.,][0-9]{3})*(?:[.,][0-9]{2})?)'
                            match = re.search(patron_precio, texto_precio)
                            if match:
                                precio_limpio = self.utils.limpiar_y_convertir_precio(match.group(1))
                                if precio_limpio and precio_limpio > 0.10:
                                    return precio_limpio
                except:
                    continue
            
            # ESTRATEGIA 2: Buscar el ÚLTIMO precio en el texto
            patron_precio = r'€\s*([0-9]{1,3}(?:[.,][0-9]{3})*(?:[.,][0-9]{2})?)'
            matches = re.findall(patron_precio, texto_completo)
            
            if matches:
                ultimo_precio_str = matches[-1]
                precio_limpio = self.utils.limpiar_y_convertir_precio(ultimo_precio_str)
                if precio_limpio and precio_limpio > 0.10:
                    return precio_limpio
            
            return 0.0
            
        except Exception as e:
            return 0.0
        
    def _extraer_nombre_legible_del_href(self, href):
            """Extrae un nombre legible del href para mostrar en los mensajes"""
            try:
                if not href or '/cards/' not in href:
                    return href
                
                partes = href.split('/cards/')
                if len(partes) > 1:
                    nombre_completo = partes[1]
                    
                    # Limpiar parámetros y extensiones
                    if '?' in nombre_completo:
                        nombre_completo = nombre_completo.split('?')[0]
                    nombre_completo = re.sub(r'\.(jpg|png|webp|jpeg)$', '', nombre_completo)
                    
                    # Tomar solo la primera parte antes de cualquier palabra de expansión
                    palabras_expansion = ['commander', 'modern', 'horizons', 'tarkir', 'dragonstorm', 'prophecy']
                    partes_nombre = nombre_completo.split('-')
                    
                    nombre_legible = []
                    for parte in partes_nombre:
                        if parte.lower() in palabras_expansion:
                            break
                        if parte.isdigit() and len(parte) <= 3:
                            break
                        nombre_legible.append(parte)
                    
                    if nombre_legible:
                        nombre = ' '.join(nombre_legible)
                        nombre = nombre.replace('-', ' ')
                        nombre = re.sub(r"\b(s)\b", "'s", nombre)
                        nombre = nombre.title()
                        return nombre
                
                return href
            except:
                return href

    def _extraer_nombre_ingles(self, elemento):
        """Extrae el nombre en inglés del href del enlace"""
        try:
            # Buscar el enlace principal que contiene el href con el nombre en inglés
            enlaces = elemento.find_elements(By.TAG_NAME, "a")
            for enlace in enlaces:
                href = enlace.get_attribute('href')
                if href and '/cards/' in href:
                    # Devolver el href completo para la comparación
                    return href
            
            return None
            
        except Exception as e:
            return None

    def _normalizar_nombre_para_comparacion(self, texto):
        """
        Normaliza un nombre para comparación, manejando específicamente:
        - Guiones: los convierte a espacios (Elder Deep-Fiend -> Elder Deep Fiend)
        - Apóstrofes posesivos: los convierte a espacios (Card's -> Card s, Temple's -> Temple s)
        - Apóstrofes plurales: los convierte a espacios (Titans' -> Titans s)
        - Guiones: también acepta eliminarlos (Card-Magic -> CardMagic)
        - Otros símbolos: los elimina
        """
        if not texto:
            return ""
        
        # Convertir a minúsculas
        texto = texto.lower()
        
        # Eliminar acentos y caracteres especiales
        texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
        
        # PRIMERO: Manejar casos específicos de apóstrofes
        # Reemplazar 's por s (posesivo: Card's -> Card s, Temple's -> Temple s)
        texto = re.sub(r"'s\b", " s", texto)
        # Reemplazar s' por s (plural posesivo: Titans' -> Titans s)
        texto = re.sub(r"s'\b", "s s", texto)
        # Reemplazar ' al final de palabra por espacio (otros casos de apóstrofes)
        texto = re.sub(r"'\b", " ", texto)
        # Reemplazar ' al principio de palabra por espacio
        texto = re.sub(r"\b'", " ", texto)
        
        # SEGUNDO: Convertir guiones a espacios (Elder Deep-Fiend -> Elder Deep Fiend)
        texto = texto.replace('-', ' ')
        
        # TERCERO: Eliminar otros símbolos especiales
        simbolos_a_eliminar = r'["_\.!@#$%^&*()\+=\[\]{}|;:,<>?/`~]'
        texto = re.sub(simbolos_a_eliminar, '', texto)
        
        # CUARTO: Reemplazar múltiples espacios por un solo espacio y eliminar espacios al inicio/final
        texto = re.sub(r'\s+', ' ', texto).strip()
        
        return texto

    def _coincidencia_exacta_ignorando_simbolos(self, href_encontrado, nombre_buscado):
        """
        Verifica si el href contiene el nombre buscado, ignorando símbolos especiales
        como -, _, ', etc. Ahora acepta múltiples variaciones:
        - Card's -> Card s
        - Card-Magic -> Card Magic O CardMagic
        - Temple's -> Temple s
        """
        try:
            # Normalizar ambos nombres para comparación
            nombre_buscado_normalizado = self._normalizar_nombre_para_comparacion(nombre_buscado)
            href_normalizado = self._normalizar_nombre_para_comparacion(href_encontrado)
            
            # Verificar si el href normalizado contiene el nombre buscado normalizado
            if nombre_buscado_normalizado and href_normalizado and nombre_buscado_normalizado in href_normalizado:
                return True
            
            # ESTRATEGIA ALTERNATIVA: También aceptar sin espacios (Card-Magic -> CardMagic)
            nombre_sin_espacios = nombre_buscado_normalizado.replace(' ', '')
            href_sin_espacios = href_normalizado.replace(' ', '')
            
            if nombre_sin_espacios and href_sin_espacios and nombre_sin_espacios in href_sin_espacios:
                return True
            
            return False
            
        except Exception as e:
            return False

    def _busqueda_alternativa_cartas(self, nombre_carta):
        """Búsqueda alternativa de cartas con filtro de número"""
        cartas = []
        try:
            elementos_carta = self.driver.find_elements(By.CSS_SELECTOR, ".blueprint-card, .product, [class*='card']")
            for elemento in elementos_carta[:25]:
                try:
                    texto = elemento.text.strip()
                    if texto and len(texto) > 20 and self.utils.coincidencia_flexible(texto, nombre_carta):
                        carta = self._extraer_carta_desde_contenedor(elemento, nombre_carta)
                        if carta and carta['precio'] > 0.10:
                            cartas.append(carta)
                except:
                    continue
        except:
            pass
        return cartas