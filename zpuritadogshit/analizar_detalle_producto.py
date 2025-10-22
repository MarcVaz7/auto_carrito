from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import re

def analizar_pagina_detalle():
    print("=== ANALIZANDO PÁGINA DE DETALLE CON VENDEDORES ===")
    
    # Configurar Chrome
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Ir a la página de detalle
        url = "https://www.cardtrader.com/cards/demonic-tutor-commander-masters"
        driver.get(url)
        time.sleep(5)
        
        print("✓ Página de detalle cargada")
        print(f"Título: {driver.title}")
        
        # 1. IDENTIFICAR LA TABLA/CONTENEDOR DE VENDEDORES
        print("\n" + "="*50)
        print("1. BUSCANDO CONTENEDOR PRINCIPAL DE VENDEDORES")
        print("="*50)
        
        # Buscar posibles contenedores de la lista de vendedores
        selectores_contenedores = [
            "table", "tbody", "thead", "tr",
            "div[class*='table']", "div[class*='list']", "div[class*='vendor']", 
            "div[class*='seller']", "div[class*='offer']", "div[class*='listing']",
            "ul", "ol", "li"
        ]
        
        for selector in selectores_contenedores:
            elementos = driver.find_elements(By.CSS_SELECTOR, selector)
            if elementos:
                # Filtrar elementos que contengan información relevante
                elementos_relevantes = []
                for elem in elementos:
                    texto = elem.text
                    if len(texto) > 50 and ('€' in texto or 'Zero' in texto or 'Add' in texto):
                        elementos_relevantes.append(elem)
                
                if elementos_relevantes:
                    print(f"Selector '{selector}': {len(elementos_relevantes)} elementos relevantes")
                    for i, elem in enumerate(elementos_relevantes[:2]):
                        print(f"  Ejemplo {i+1}:")
                        print(f"    Texto: {elem.text[:200]}...")
                        print(f"    Clase: {elem.get_attribute('class')}")
        
        # 2. IDENTIFICAR PRECIOS Y ORDENAR POR MÁS BAJO
        print("\n" + "="*50)
        print("2. ANALIZANDO PRECIOS Y ESTRUCTURA DE COSTOS")
        print("="*50)
        
        # Buscar todos los precios
        precios = driver.find_elements(By.XPATH, "//*[contains(text(), '€')]")
        print(f"Elementos con '€' encontrados: {len(precios)}")
        
        precios_limpios = []
        for precio in precios:
            texto = precio.text.strip()
            if '€' in texto and any(c.isdigit() for c in texto):
                # Extraer valor numérico
                match = re.search(r'€\s*([0-9]+[.,][0-9]+)', texto)
                if match:
                    valor = float(match.group(1).replace(',', '.'))
                    precios_limpios.append({
                        'elemento': precio,
                        'texto': texto,
                        'valor': valor,
                        'html': precio.get_attribute('outerHTML')[:100] + "..."
                    })
        
        # Ordenar por precio más bajo
        precios_limpios.sort(key=lambda x: x['valor'])
        
        print(f"Precios válidos encontrados: {len(precios_limpios)}")
        for i, precio in enumerate(precios_limpios[:10]):
            print(f"  {i+1}. €{precio['valor']:.2f} - {precio['texto']}")
        
        # 3. IDENTIFICAR UBICACIÓN/VENDEDORES UE
        print("\n" + "="*50)
        print("3. BUSCANDO INFORMACIÓN DE UBICACIÓN/VENDEDOR")
        print("="*50)
        
        # Buscar banderas, países, ubicaciones
        ubicaciones_claves = ["EU", "Europe", "European", "Spain", "France", "Germany", "Italy", "Portugal", "European Union"]
        elementos_ubicacion = []
        
        for ubicacion in ubicaciones_claves:
            elementos = driver.find_elements(By.XPATH, f"//*[contains(text(), '{ubicacion}') or contains(@class, '{ubicacion.lower()}')]")
            if elementos:
                print(f"Elementos con '{ubicacion}': {len(elementos)}")
                for elem in elementos[:2]:
                    print(f"  - Texto: {elem.text}")
                    print(f"    Clase: {elem.get_attribute('class')}")
                    elementos_ubicacion.append(elem)
        
        # Buscar banderas (imágenes)
        banderas = driver.find_elements(By.CSS_SELECTOR, "img[src*='flag'], img[alt*='flag'], img[class*='flag']")
        print(f"Posibles banderas encontradas: {len(banderas)}")
        for bandera in banderas[:3]:
            print(f"  - src: {bandera.get_attribute('src')}")
            print(f"    alt: {bandera.get_attribute('alt')}")
        
        # 4. IDENTIFICAR BOTÓN "ZERO"
        print("\n" + "="*50)
        print("4. BUSCANDO BOTÓN ZERO Y OPCIONES DE ENVÍO")
        print("="*50)
        
        # Buscar específicamente "Zero"
        elementos_zero = driver.find_elements(By.XPATH, "//*[contains(text(), 'Zero') or contains(@class, 'zero')]")
        print(f"Elementos con 'Zero': {len(elementos_zero)}")
        
        for elemento in elementos_zero:
            texto = elemento.text
            if 'Zero' in texto:
                print(f"  - Texto: {texto}")
                print(f"    Clase: {elemento.get_attribute('class')}")
                print(f"    Tag: {elemento.tag_name}")
                
                # Verificar si es un botón clickeable
                try:
                    padre = elemento.find_element(By.XPATH, "./..")
                    print(f"    Padre: {padre.tag_name} - Clase: {padre.get_attribute('class')}")
                except:
                    print("    No se pudo obtener información del padre")
        
        # 5. IDENTIFICAR BOTONES "ADD TO CART"
        print("\n" + "="*50)
        print("5. ANALIZANDO BOTONES DE AÑADIR AL CARRITO")
        print("="*50)
        
        textos_botones = ["Add to Cart", "Añadir", "Add", "Cart", "Comprar", "Buy"]
        for texto in textos_botones:
            botones = driver.find_elements(By.XPATH, f"//*[contains(text(), '{texto}')]")
            if botones:
                print(f"Botones con '{texto}': {len(botones)}")
                for boton in botones[:2]:
                    print(f"  - Texto completo: {boton.text}")
                    print(f"    Clase: {boton.get_attribute('class')}")
                    print(f"    Tag: {boton.tag_name}")
                    
                    # Verificar si está habilitado
                    try:
                        if boton.get_attribute('disabled'):
                            print(f"    ⚠️ ESTÁ DESHABILITADO")
                        else:
                            print(f"    ✅ ESTÁ HABILITADO")
                    except:
                        print(f"    ✅ POSIBLEMENTE HABILITADO")
        
        # 6. IDENTIFICAR CONDICIONES DE LA CARTA
        print("\n" + "="*50)
        print("6. BUSCANDO CONDICIONES DE LA CARTA (NM, LP, etc)")
        print("="*50)
        
        condiciones = ["Near Mint", "NM", "Lightly Played", "LP", "Moderately Played", "MP", "Heavily Played", "HP"]
        for condicion in condiciones:
            elementos = driver.find_elements(By.XPATH, f"//*[contains(text(), '{condicion}')]")
            if elementos:
                print(f"Elementos con '{condicion}': {len(elementos)}")
                for elem in elementos[:2]:
                    print(f"  - Texto: {elem.text}")
        
        # 7. ESTRUCTURA COMPLETA DE UNA FILA DE VENDEDOR
        print("\n" + "="*50)
        print("7. ANALIZANDO ESTRUCTURA COMPLETA DE FILAS")
        print("="*50)
        
        # Buscar filas que contengan múltiples elementos (precio, botón, etc.)
        filas_completas = driver.find_elements(By.CSS_SELECTOR, "tr, div[class*='row'], li")
        filas_con_info = []
        
        for fila in filas_completas:
            texto = fila.text
            if len(texto) > 30 and ('€' in texto or 'Add' in texto or 'Zero' in texto):
                filas_con_info.append(fila)
        
        print(f"Filas completas con información: {len(filas_con_info)}")
        
        if filas_con_info:
            primera_fila = filas_con_info[0]
            print("PRIMERA FILA COMPLETA:")
            print(f"Texto: {primera_fila.text}")
            print(f"Clase: {primera_fila.get_attribute('class')}")
            
            # Analizar elementos hijos
            hijos = primera_fila.find_elements(By.XPATH, ".//*")
            print(f"Elementos hijos: {len(hijos)}")
            
            # Agrupar por tipo
            tipos_elementos = {}
            for hijo in hijos:
                tag = hijo.tag_name
                if tag not in tipos_elementos:
                    tipos_elementos[tag] = 0
                tipos_elementos[tag] += 1
            
            print(f"Distribución de tags: {tipos_elementos}")
        
        # 8. BUSCAR SELECTORES ESPECÍFICOS
        print("\n" + "="*50)
        print("8. SELECTORES CSS ESPECÍFICOS")
        print("="*50)
        
        elementos_con_clases = driver.find_elements(By.CSS_SELECTOR, "[class]")
        clases_interesantes = set()
        
        for elemento in elementos_con_clases:
            clase = elemento.get_attribute('class')
            if any(keyword in clase.lower() for keyword in ['price', 'zero', 'cart', 'add', 'vendor', 'seller', 'ship', 'flag', 'condition', 'location']):
                clases_interesantes.add(clase)
        
        print("Clases interesantes encontradas:")
        for clase in sorted(clases_interesantes):
            print(f"  - {clase}")
        
        # Guardar screenshot para referencia
        driver.save_screenshot("detalle_vendedores.png")
        print("\n✓ Screenshot guardado como 'detalle_vendedores.png'")
        
        # Guardar HTML de una sección específica
        with open("seccion_vendedores.html", "w", encoding="utf-8") as f:
            if filas_con_info:
                f.write(filas_con_info[0].get_attribute('outerHTML'))
            else:
                f.write(driver.page_source[:5000])
        print("✓ HTML de sección guardado como 'seccion_vendedores.html'")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()

if __name__ == "__main__":
    analizar_pagina_detalle()