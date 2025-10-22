from abc import ABC, abstractmethod
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import urllib.parse
import getpass
from config_manager import ConfigManager

class PlatformBase(ABC):
    def __init__(self, driver, utils):
        self.driver = driver
        self.utils = utils
        self.config_manager = ConfigManager()
    
    @abstractmethod
    def login(self):
        pass
    
    @abstractmethod
    def buscar_carta(self, nombre_carta):
        pass
    
    @abstractmethod
    def seleccionar_carta_mas_barata(self, nombre_carta):
        pass
    
    @abstractmethod
    def buscar_vendedores(self, condiciones, cantidad_necesaria=1):
        pass

    def _ya_esta_logueado(self):
        """Verifica si ya hay una sesión activa"""
        try:
            # Buscar elementos que indican que el usuario está logueado
            elementos_logueado = [
                "//a[contains(@href, '/users/sign_out')]",
                "//a[contains(text(), 'Mi cuenta')]",
                "//a[contains(text(), 'My account')]"
            ]
            
            for elemento in elementos_logueado:
                try:
                    if self.driver.find_elements(By.XPATH, elemento):
                        return True
                except:
                    continue
            return False
        except:
            return False

    def _pedir_credenciales_interactivo(self, platform):
        """Pide credenciales al usuario de forma interactiva"""
        print(f"\n🔐 Credenciales necesarias para {platform.upper()}")
        print("Por favor, ingresa tus datos de acceso:")
        
        username = input("Usuario/Email: ").strip()
        password = getpass.getpass("Contraseña: ").strip()
        
        if not username or not password:
            print("❌ Se requieren tanto usuario como contraseña")
            return False
        
        # Guardar credenciales
        if self.config_manager.set_credentials(platform, username, password):
            print("✅ Credenciales guardadas")
            # Intentar login nuevamente
            return self.login()
        else:
            print("❌ Error guardando credenciales")
            return False