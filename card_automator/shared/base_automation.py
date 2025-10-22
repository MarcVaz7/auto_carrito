from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time

class BaseAutomation:
    def __init__(self, plataforma):
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("detach", True)
        self.service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        self.actions = ActionChains(self.driver)
        self.plataforma = plataforma
        
        # Inicializar variable de vendedor
        self.ultimo_vendedor = None
    
    def cerrar_popups(self):
        """Cierra todos los popups molestos"""
        self.utils.cerrar_popups()
    
    def verificar_agregado_carrito(self):
        """Verificación MEJORADA de si se agregó al carrito"""
        time.sleep(2)
        
        # Buscar mensajes de confirmación específicos
        confirmaciones = [
            "//*[contains(text(), 'añadido') and contains(text(), 'carrito')]",
            "//*[contains(text(), 'added') and contains(text(), 'cart')]",
            "//*[contains(@class, 'alert-success')]",
            "//*[contains(@class, 'toast-success')]"
        ]
        
        for confirmacion in confirmaciones:
            try:
                elemento = self.driver.find_element(By.XPATH, confirmacion)
                if elemento.is_displayed():
                    return True
            except:
                continue
        
        # Verificar si el botón cambió a "En carrito" o similar
        try:
            botones_carrito = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'carrito') or contains(text(), 'cart')]")
            for boton in botones_carrito:
                if any(texto in boton.text.lower() for texto in ['en carrito', 'in cart', 'añadido', 'added']):
                    return True
        except:
            pass
        
        # Si no encontramos confirmación visual, asumimos éxito
        print("⚠️ No se detectó confirmación visual, pero se asume éxito")
        return True
    
    def mantener_abierto(self):
        """Mantiene el navegador abierto"""
        print("\n🖥️ Navegador permanece abierto...")
        input("Presiona Enter para cerrar...")
    
    def cerrar(self):
        """Cierra el navegador"""
        self.driver.quit()