from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import json

def identificar_productos_reales():
    print("=== IDENTIFICANDO PRODUCTOS REALES ===")
    
    # Configurar Chrome
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Ir a la búsqueda
        url = "https://www.cardtrader.com/games/magic/categories/magic-single-card/blueprints_search?sort=name+asc&blueprints_search[name_en_or_name_es_cont]=demonic%20tutor"
        driver.get(url)
        time.sleep(5)
        
        print("✓ Página cargada correctamente")
        print(f"Título: {driver.title}")
        
        # ESTRATEGIA 1: Buscar elementos que contengan información de cartas
        print("\n=== BUSCANDO CARTAS ESPECÍFICAS ===")
        
        # Buscar por texto que contenga "Demonic Tutor"
        elementos_con_texto = driver.find_elements(By.XPATH, "//*[contains(text(), 'Demonic Tutor')]")
        print(f"Elementos que contienen 'Demonic Tutor': {len(elementos_con_texto)}")
        
        for i, elemento in enumerate(elementos_con_texto[:5]):
            print(f"  {i+1}. Texto: {elemento.text[:100]}...")
            print(f"     Clase: {elemento.get_attribute('class')}")
            print(f"     Tag: {elemento.tag_name}")
            print("     ---")
        
        # ESTRATEGIA 2: Buscar contenedores probables
        print("\n=== BUSCANDO CONTENEDORES DE PRODUCTOS ===")
        
        selectores_contenedores = [
            "div.card", "article", "section", "li", "tr",
            "div[class*='product']", "div[class*='item']", "div[class*='listing']",
            "div[class*='blueprint']", "div[class*='offer']"
        ]
        
        for selector in selectores_contenedores:
            elementos = driver.find_elements(By.CSS_SELECTOR, selector)
            if elementos:
                print(f"Selector '{selector}': {len(elementos)} elementos")
                
                # Analizar los primeros 2 elementos
                for i, elem in enumerate(elementos[:2]):
                    texto = elem.text.replace('\n', ' | ')
                    if texto and len(texto) > 10:  # Solo mostrar si tiene texto significativo
                        print(f"  Ejemplo {i+1}: {texto[:150]}...")
        
        # ESTRATEGIA 3: Buscar precios específicamente
        print("\n=== PRECIOS DETALLADOS ===")
        
        # Buscar elementos que contengan €
        elementos_euro = driver.find_elements(By.XPATH, "//*[contains(text(), '€')]")
        print(f"Elementos con '€': {len(elementos_euro)}")
        
        for i, precio in enumerate(elementos_euro[:10]):
            texto_precio = precio.text.strip()
            if texto_precio and '€' in texto_precio:
                # Intentar encontrar el elemento padre para contexto
                padre = precio.find_element(By.XPATH, "./..")
                clases_padre = padre.get_attribute('class')
                print(f"  Precio {i+1}: {texto_precio}")
                print(f"     Clase del contenedor: {clases_padre}")
        
        # ESTRATEGIA 4: Buscar botones de "Add to Cart" específicos
        print("\n=== BOTONES DE COMPRA ===")
        
        textos_botones = ["Add to Cart", "Añadir", "Comprar", "Add", "Cart", "Buy", "Purchase"]
        for texto in textos_botones:
            try:
                botones = driver.find_elements(By.XPATH, f"//*[contains(text(), '{texto}')]")
                if botones:
                    print(f"Botones con texto '{texto}': {len(botones)}")
            except:
                pass
        
        # Guardar HTML completo para análisis manual
        with open("pagina_completa.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("✓ HTML guardado como 'pagina_completa.html'")
        
        # Tomar screenshot del viewport completo
        driver.save_screenshot("vista_completa.png")
        print("✓ Screenshot guardado como 'vista_completa.png'")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.quit()

def buscar_patrones_especificos():
    """Función adicional para patrones comunes en tiendas de cartas"""
    print("\n=== PATRONES ESPECÍFICOS PARA CARDTRADER ===")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    
    try:
        driver.get("https://www.cardtrader.com/games/magic/categories/magic-single-card/blueprints_search?sort=name+asc&blueprints_search[name_en_or_name_es_cont]=demonic%20tutor")
        time.sleep(5)
        
        # Patrón 1: Buscar tablas (común en listados de cartas)
        tablas = driver.find_elements(By.TAG_NAME, "table")
        print(f"Tablas encontradas: {len(tablas)}")
        
        # Patrón 2: Buscar grid de productos
        grids = driver.find_elements(By.CSS_SELECTOR, "[class*='grid'], [class*='row']")
        print(f"Elementos grid/row: {len(grids)}")
        
        # Patrón 3: Buscar elementos con datos de producto
        elementos_con_data = driver.find_elements(By.CSS_SELECTOR, "[data-*], [id*='product'], [id*='item']")
        print(f"Elementos con atributos data/id: {len(elementos_con_data)}")
        
    except Exception as e:
        print(f"Error en patrones: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    identificar_productos_reales()
    buscar_patrones_especificos()