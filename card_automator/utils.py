import time
import re
import unicodedata
from selenium.webdriver.common.by import By

class Utils:
    def __init__(self, driver):
        self.driver = driver
    
    def cerrar_popups(self):
        """Cierra todos los popups molestos"""
        try:
            popup_selectors = [
                ".iubenda-cs-close-btn",
                "button[iubenda-cc-close]",
                "#iubenda-cs-banner button",
            ]
            
            for selector in popup_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            element.click()
                            time.sleep(0.5)
                except:
                    continue
                    
            # JavaScript adicional para asegurar
            self.driver.execute_script("""
                var closeButtons = document.querySelectorAll('.iubenda-cs-close-btn, [iubenda-cc-close]');
                closeButtons.forEach(function(btn) { if(btn) btn.click(); });
            """)
        except Exception as e:
            pass
    
    def limpiar_y_convertir_precio(self, precio_str):
        """Limpia y convierte un string de precio a float de forma robusta"""
        if not precio_str:
            return None
        
        # Eliminar espacios
        precio_str = precio_str.strip()
        
        # Caso 1: Tiene tanto punto como coma 
        if '.' in precio_str and ',' in precio_str:
            # Determinar cuál es separador de miles y cuál decimal basado en la posición
            ultimo_punto = precio_str.rfind('.')
            ultima_coma = precio_str.rfind(',')
            
            # Si el punto está después de la coma -> formato 3,500.64 (coma=miles, punto=decimal)
            if ultimo_punto > ultima_coma:
                precio_limpio = precio_str.replace(',', '')  # Eliminar comas (miles)
            # Si la coma está después del punto -> formato 3.500,64 (punto=miles, coma=decimal)  
            else:
                precio_limpio = precio_str.replace('.', '').replace(',', '.')  # Puntos=miles, coma=decimal
        
        # Caso 2: Solo tiene coma
        elif ',' in precio_str:
            partes = precio_str.split(',')
            # Si después de la coma hay 3 dígitos -> probablemente es separador de miles (1,000)
            if len(partes) > 1 and len(partes[-1]) == 3 and len(partes[0]) <= 3:
                precio_limpio = precio_str.replace(',', '')  # Eliminar comas (miles)
            # Si después de la coma hay 2 dígitos -> probablemente es decimal (1,50)
            elif len(partes) > 1 and len(partes[-1]) == 2:
                precio_limpio = precio_str.replace(',', '.')  # Convertir coma a punto decimal
            else:
                # Por defecto, asumir que es separador de miles
                precio_limpio = precio_str.replace(',', '')
        
        # Caso 3: Solo tiene punto
        elif '.' in precio_str:
            partes = precio_str.split('.')
            # Si después del punto hay 3 dígitos -> probablemente es separador de miles (1.000)
            if len(partes) > 1 and len(partes[-1]) == 3 and len(partes[0]) <= 3:
                precio_limpio = precio_str.replace('.', '')  # Eliminar puntos (miles)
            # Si después del punto hay 2 dígitos -> probablemente es decimal (1.50)
            elif len(partes) > 1 and len(partes[-1]) == 2:
                precio_limpio = precio_str  # Mantener como está (punto decimal)
            else:
                # Por defecto, asumir que es decimal
                precio_limpio = precio_str
        
        # Caso 4: Sin separadores
        else:
            precio_limpio = precio_str
        
        # Convertir a float
        try:
            resultado = float(precio_limpio)
            return resultado
        except:
            return None

    def limpiar_y_convertir_precio_cardmarket(self, precio_str):
        """Limpia precios específicos de CardMarket (formato europeo)"""
        if not precio_str:
            return None
        
        # CardMarket usa formato europeo: 0,40 €
        precio_str = precio_str.strip()
        
        # Eliminar símbolo € y espacios
        precio_str = precio_str.replace('€', '').strip()
        
        # Reemplazar coma por punto para decimales
        precio_str = precio_str.replace(',', '.')
        
        # Eliminar puntos de miles (si los hay)
        if '.' in precio_str:
            partes = precio_str.split('.')
            if len(partes) > 2:  # Tiene separadores de miles
                precio_str = partes[0] + partes[1] + '.' + partes[2]
            elif len(partes) == 2 and len(partes[1]) > 2:  # Probable separador de miles
                precio_str = partes[0] + partes[1]
        
        try:
            return float(precio_str)
        except:
            return None
    
    def coincidencia_flexible(self, texto, busqueda):
        """Coincidencia flexible del nombre"""
        texto_limpio = texto.lower()
        busqueda_limpia = busqueda.lower()
        
        if busqueda_limpia in texto_limpio:
            return True
        
        palabras_busqueda = [p for p in re.findall(r'\w+', busqueda_limpia) if len(p) > 3]
        palabras_texto = [p for p in re.findall(r'\w+', texto_limpio) if len(p) > 3]
        
        if not palabras_busqueda:
            return False
        
        coincidencias = sum(1 for pb in palabras_busqueda if any(pt == pb for pt in palabras_texto))
        return coincidencias >= len(palabras_busqueda) * 0.6

    def normalizar_nombre_para_comparacion(self, texto):
        """
        Normaliza un nombre para comparación, manejando específicamente:
        - Guiones: los convierte a espacios (Elder Deep-Fiend -> Elder Deep Fiend)
        - Apóstrofes posesivos: los elimina (Talisman's -> Talismans)
        - Apóstrofes plurales: los elimina (Titans' -> Titans)
        - Otros símbolos: los elimina
        """
        if not texto:
            return ""
        
        # Convertir a minúsculas
        texto = texto.lower()
        
        # Eliminar acentos y caracteres especiales
        texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
        
        # PRIMERO: Manejar casos específicos de apóstrofes
        # Reemplazar 's por s (posesivo: Talisman's -> Talismans)
        texto = re.sub(r"'s\b", "s", texto)
        # Reemplazar s' por s (plural posesivo: Titans' -> Titans)
        texto = re.sub(r"s'\b", "s", texto)
        # Reemplazar ' al final de palabra por nada (otros casos de apóstrofes)
        texto = re.sub(r"'\b", "", texto)
        # Reemplazar ' al principio de palabra por nada
        texto = re.sub(r"\b'", "", texto)
        
        # SEGUNDO: Convertir guiones a espacios (Elder Deep-Fiend -> Elder Deep Fiend)
        texto = texto.replace('-', ' ')
        
        # TERCERO: Eliminar otros símbolos especiales
        simbolos_a_eliminar = r'["_\.!@#$%^&*()\+=\[\]{}|;:,<>?/`~]'
        texto = re.sub(simbolos_a_eliminar, '', texto)
        
        # CUARTO: Reemplazar múltiples espacios por un solo espacio y eliminar espacios al inicio/final
        texto = re.sub(r'\s+', ' ', texto).strip()
        
        return texto
    def limpiar_y_convertir_precio_cardmarket(self, precio_str):
        """Limpia precios específicos de CardMarket (formato europeo)"""
        if not precio_str:
            return None
        
        # CardMarket usa formato europeo: 0,40 €
        precio_str = precio_str.strip()
        
        # Eliminar símbolo € y espacios
        precio_str = precio_str.replace('€', '').strip()
        
        # Reemplazar coma por punto para decimales
        precio_str = precio_str.replace(',', '.')
        
        # Eliminar puntos de miles (si los hay)
        if '.' in precio_str:
            partes = precio_str.split('.')
            if len(partes) > 2:  # Tiene separadores de miles
                precio_str = partes[0] + partes[1] + '.' + partes[2]
            elif len(partes) == 2 and len(partes[1]) > 2:  # Probable separador de miles
                precio_str = partes[0] + partes[1]
        
        try:
            return float(precio_str)
        except:
            return None