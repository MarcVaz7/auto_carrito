from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time

def analizar_estructura():
    # Configurar Chrome
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    
    try:
        # Ir a la búsqueda de Demonic Tutor
        url = "https://www.cardtrader.com/games/magic/categories/magic-single-card/blueprints_search?sort=name+asc&blueprints_search[name_en_or_name_es_cont]=demonic%20tutor"
        driver.get(url)
        time.sleep(3)  # Esperar a que cargue
        
        print("=== ANALIZANDO ESTRUCTURA DE LA WEB ===")
        
        # 1. Buscar contenedores de productos
        productos = driver.find_elements(By.CSS_SELECTOR, "[class*='product'], [class*='card'], [class*='item']")
        print(f"Elementos que podrían ser productos: {len(productos)}")
        
        # 2. Mostrar clases de los primeros elementos
        for i, elemento in enumerate(productos[:5]):
            print(f"Elemento {i+1}: Clase = '{elemento.get_attribute('class')}'")
        
        # 3. Buscar precios
        precios = driver.find_elements(By.CSS_SELECTOR, "[class*='price'], [class*='cost']")
        print(f"\nElementos que podrían ser precios: {len(precios)}")
        
        # 4. Buscar botones de agregar al carrito
        botones = driver.find_elements(By.CSS_SELECTOR, "button, [class*='btn'], [class*='button'], [class*='add'], [class*='cart']")
        print(f"Botones encontrados: {len(botones)}")
        
        # 5. Tomar screenshot para ver estructura
        driver.save_screenshot("estructura_web.png")
        print("✓ Screenshot guardado como 'estructura_web.png'")
        
        # 6. Mostrar HTML de algunos elementos clave
        print("\n=== HTML DE ELEMENTOS CLAVE ===")
        for i, producto in enumerate(productos[:3]):
            print(f"\n--- Producto {i+1} ---")
            print(producto.get_attribute('outerHTML')[:500] + "...")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    analizar_estructura()