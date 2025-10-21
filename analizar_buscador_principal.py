from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import json

def analizar_buscador_principal():
    print("=== ANALIZANDO BUSCADOR EN PÁGINA PRINCIPAL ===")
    
    # Configurar Chrome
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Ir a la página principal de CardTrader
        url = "https://www.cardtrader.com/es/magic"
        driver.get(url)
        time.sleep(5)
        
        print("✓ Página principal cargada correctamente")
        print(f"Título: {driver.title}")
        
        # Cerrar popups si existen
        cerrar_popups(driver)
        
        # ESTRATEGIA 1: Buscar todos los campos de entrada
        print("\n" + "="*50)
        print("1. BUSCANDO CAMPOS DE ENTRADA (INPUT)")
        print("="*50)
        
        inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"Total de inputs encontrados: {len(inputs)}")
        
        for i, input_elem in enumerate(inputs):
            try:
                input_type = input_elem.get_attribute('type')
                placeholder = input_elem.get_attribute('placeholder')
                name = input_elem.get_attribute('name')
                id_attr = input_elem.get_attribute('id')
                clase = input_elem.get_attribute('class')
                
                print(f"  Input {i+1}:")
                print(f"    Tipo: {input_type}")
                print(f"    Placeholder: '{placeholder}'")
                print(f"    Name: '{name}'")
                print(f"    ID: '{id_attr}'")
                print(f"    Clase: '{clase}'")
                print(f"    Visible: {input_elem.is_displayed()}")
                print("     ---")
            except:
                continue
        
        # ESTRATEGIA 2: Buscar específicamente campos de búsqueda
        print("\n" + "="*50)
        print("2. BUSCANDO CAMPOS DE BÚSQUEDA ESPECÍFICOS")
        print("="*50)
        
        selectores_busqueda = [
            "input[type='search']",
            "input[placeholder*='buscar']",
            "input[placeholder*='search']",
            "input[name*='search']",
            "input[name*='q']",
            "input[class*='search']",
            "#search",
            ".search-input",
            "input[aria-label*='search']",
            "input[aria-label*='buscar']"
        ]
        
        for selector in selectores_busqueda:
            try:
                elementos = driver.find_elements(By.CSS_SELECTOR, selector)
                if elementos:
                    print(f"Selector '{selector}': {len(elementos)} elementos")
                    for i, elem in enumerate(elementos):
                        if elem.is_displayed():
                            print(f"  ✅ ELEMENTO VISIBLE {i+1}:")
                            print(f"     Placeholder: '{elem.get_attribute('placeholder')}'")
                            print(f"     Name: '{elem.get_attribute('name')}'")
                            print(f"     ID: '{elem.get_attribute('id')}'")
                            print(f"     Clase: '{elem.get_attribute('class')}'")
                            print(f"     Valor: '{elem.get_attribute('value')}'")
            except:
                continue
        
        # ESTRATEGIA 3: Buscar formularios de búsqueda
        print("\n" + "="*50)
        print("3. BUSCANDO FORMULARIOS DE BÚSQUEDA")
        print("="*50)
        
        forms = driver.find_elements(By.TAG_NAME, "form")
        print(f"Formularios encontrados: {len(forms)}")
        
        for i, form in enumerate(forms):
            try:
                form_html = form.get_attribute('outerHTML')
                if 'search' in form_html.lower() or 'buscar' in form_html.lower():
                    print(f"  Formulario {i+1} (posible búsqueda):")
                    print(f"    ID: '{form.get_attribute('id')}'")
                    print(f"    Clase: '{form.get_attribute('class')}'")
                    print(f"    Action: '{form.get_attribute('action')}'")
                    
                    # Buscar inputs dentro del formulario
                    inputs_form = form.find_elements(By.TAG_NAME, "input")
                    for j, input_form in enumerate(inputs_form):
                        if input_form.is_displayed():
                            print(f"    Input {j+1}: '{input_form.get_attribute('placeholder')}'")
            except:
                continue
        
        # ESTRATEGIA 4: Buscar botones de búsqueda
        print("\n" + "="*50)
        print("4. BUSCANDO BOTONES DE BÚSQUEDA")
        print("="*50)
        
        textos_botones_busqueda = ["Buscar", "Search", "🔍", "⌕", "Go", "Find"]
        selectores_botones = [
            "button[type='submit']",
            "input[type='submit']",
            "button[class*='search']",
            "button[aria-label*='search']",
            ".search-button",
            ".btn-search"
        ]
        
        # Buscar por texto
        for texto in textos_botones_busqueda:
            try:
                botones = driver.find_elements(By.XPATH, f"//*[contains(text(), '{texto}')]")
                if botones:
                    print(f"Botones con texto '{texto}': {len(botones)}")
                    for i, boton in enumerate(botones[:3]):
                        if boton.is_displayed():
                            print(f"  ✅ BOTÓN VISIBLE {i+1}:")
                            print(f"     Texto: '{boton.text}'")
                            print(f"     Tag: {boton.tag_name}")
                            print(f"     Clase: '{boton.get_attribute('class')}'")
            except:
                continue
        
        # Buscar por selectores
        for selector in selectores_botones:
            try:
                botones = driver.find_elements(By.CSS_SELECTOR, selector)
                if botones:
                    print(f"Selector '{selector}': {len(botones)} elementos")
                    for i, boton in enumerate(botones):
                        if boton.is_displayed():
                            print(f"  ✅ BOTÓN VISIBLE {i+1}:")
                            print(f"     Texto: '{boton.text}'")
                            print(f"     Tag: {boton.tag_name}")
                            print(f"     Clase: '{boton.get_attribute('class')}'")
            except:
                continue
        
        # ESTRATEGIA 5: Identificar la estructura completa del buscador
        print("\n" + "="*50)
        print("5. ESTRUCTURA COMPLETA DEL BUSCADOR")
        print("="*50)
        
        # Buscar elementos que contengan tanto input como botón de búsqueda
        contenedores_busqueda = driver.find_elements(By.CSS_SELECTOR, ".search-form, form[role='search'], [class*='search']")
        print(f"Contenedores de búsqueda encontrados: {len(contenedores_busqueda)}")
        
        for i, contenedor in enumerate(contenedores_busqueda):
            if contenedor.is_displayed():
                print(f"  Contenedor {i+1}:")
                print(f"    Clase: '{contenedor.get_attribute('class')}'")
                
                # Buscar input dentro del contenedor
                inputs_cont = contenedor.find_elements(By.TAG_NAME, "input")
                for input_cont in inputs_cont:
                    if input_cont.is_displayed():
                        print(f"    📝 INPUT: '{input_cont.get_attribute('placeholder')}'")
                
                # Buscar botón dentro del contenedor
                botones_cont = contenedor.find_elements(By.TAG_NAME, "button")
                for boton_cont in botones_cont:
                    if boton_cont.is_displayed():
                        print(f"    🔘 BOTÓN: '{boton_cont.text}'")
        
        # ESTRATEGIA 6: Probar el buscador principal manualmente
        print("\n" + "="*50)
        print("6. PRUEBA MANUAL DEL BUSCADOR")
        print("="*50)
        
        # Intentar encontrar y usar el buscador más prometedor
        candidatos_buscador = [
            "input[placeholder*='buscar']",
            "input[placeholder*='search']", 
            "input[name*='search']",
            "input[type='search']"
        ]
        
        for selector in candidatos_buscador:
            try:
                input_buscador = driver.find_element(By.CSS_SELECTOR, selector)
                if input_buscador.is_displayed():
                    print(f"🎯 PROBANDO BUSCADOR: {selector}")
                    input_buscador.clear()
                    input_buscador.send_keys("Demonic Tutor")
                    time.sleep(2)
                    
                    # Buscar botón de envío asociado
                    try:
                        # Buscar botón en el mismo formulario
                        form_padre = input_buscador.find_element(By.XPATH, "./ancestor::form")
                        boton = form_padre.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
                        if boton.is_displayed():
                            print(f"   ✅ Botón encontrado: '{boton.text}'")
                            # boton.click()  # Comentado para no ejecutar la búsqueda real
                    except:
                        print("   ℹ️ No se encontró botón específico, probar con ENTER")
                    
                    input_buscador.clear()
                    break
            except:
                continue
        
        # Guardar recursos para análisis
        with open("pagina_principal_cardtrader.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("✓ HTML guardado como 'pagina_principal_cardtrader.html'")
        
        driver.save_screenshot("vista_principal.png")
        print("✓ Screenshot guardado como 'vista_principal.png'")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()

def cerrar_popups(driver):
    """Cierra popups de cookies si existen"""
    try:
        popup_selectors = [
            ".iubenda-cs-close-btn",
            "button[iubenda-cc-close]",
            "#iubenda-cs-banner button",
            "button[aria-label*='cookie']",
            "button[aria-label*='Cookie']",
        ]
        
        for selector in popup_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed():
                        element.click()
                        print(f"✅ Popup cerrado: {selector}")
                        time.sleep(1)
            except:
                continue
    except Exception as e:
        print(f"ℹ️ No se pudieron cerrar popups: {e}")

def analizar_navegacion():
    """Analiza la estructura de navegación del sitio"""
    print("\n" + "="*50)
    print("ANÁLISIS DE NAVEGACIÓN Y ESTRUCTURA")
    print("="*50)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    
    try:
        driver.get("https://www.cardtrader.com/es/magic")
        time.sleep(5)
        cerrar_popups(driver)
        
        # Buscar elementos de navegación
        nav_elements = driver.find_elements(By.CSS_SELECTOR, "nav, header, .navbar, .header")
        print(f"Elementos de navegación: {len(nav_elements)}")
        
        for i, nav in enumerate(nav_elements):
            if nav.is_displayed():
                print(f"  Navegación {i+1}:")
                print(f"    Clase: '{nav.get_attribute('class')}'")
                
                # Buscar buscador dentro de la navegación
                buscadores_nav = nav.find_elements(By.CSS_SELECTOR, "input[placeholder*='search'], input[placeholder*='buscar']")
                if buscadores_nav:
                    print(f"    ✅ TIENE BUSCADOR: {len(buscadores_nav)} elementos")
        
    except Exception as e:
        print(f"Error en análisis de navegación: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    analizar_buscador_principal()
    analizar_navegacion()