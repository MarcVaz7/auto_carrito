from cardtrader.cardtrader_automation import CardTraderAutomation
from cardmarket.cardmarket_automation import CardMarketAutomation
from config_manager import ConfigManager
from login_dialog import LoginDialog
import time
from selenium.webdriver.common.by import By
import tkinter as tk

class CardAutomation:
    def __init__(self, plataforma="cardtrader"):
        self.plataforma = plataforma.lower()
        self.config_manager = ConfigManager()
        
        # Primero crear la instancia de automation
        if self.plataforma == "cardmarket":
            self.automation = CardMarketAutomation()
            print("🌐 Plataforma: CardMarket seleccionada")
        else:
            self.automation = CardTraderAutomation()
            print("🌐 Plataforma: CardTrader seleccionada (por defecto)")
        
        # Delegar métodos al automation específico
        self.driver = self.automation.driver
        self.utils = self.automation.utils
        
        # NUEVO: Iniciar sesión automáticamente DESPUÉS de crear automation
        self._iniciar_sesion_automatica()

    def buscar_en_vendedor_prioritario(self, nombre_carta, vendedor, condiciones, cantidad_necesaria=1):
        """Busca una carta en un vendedor prioritario - delega al automation específico"""
        if hasattr(self.automation, 'buscar_en_vendedor_prioritario'):
            return self.automation.buscar_en_vendedor_prioritario(
                nombre_carta, vendedor, condiciones, cantidad_necesaria
            )
        else:
            print(f"❌ Plataforma {self.plataforma} no soporta búsqueda en vendedores prioritarios")
            return False
    
    def _iniciar_sesion_automatica(self):
        """Intenta iniciar sesión automáticamente con credenciales guardadas"""
        print(f"\n🔐 Intentando inicio de sesión automático en {self.plataforma}...")
        
        # Verificar si existen credenciales
        if not self.config_manager.has_credentials(self.plataforma):
            print("❌ No hay credenciales guardadas. Se necesitará login manual.")
            print("💡 Usa forzar_login_manual() para configurar credenciales")
            return False
        
        # Obtener credenciales
        credenciales = self.config_manager.get_credentials(self.plataforma)
        username = credenciales.get('username')
        password = credenciales.get('password')
        
        if not username or not password:
            print("❌ Credenciales incompletas.")
            return False
            
        print(f"✅ Credenciales encontradas para: {username}")
        
        try:
            # Navegar a la página de login
            if self.plataforma == "cardmarket":
                login_url = "https://www.cardmarket.com/es/Magic/Login"
            else:
                login_url = "https://cardtrader.com/users/sign_in"
            
            print(f"🌐 Navegando a: {login_url}")
            self.driver.get(login_url)
            time.sleep(3)
            
            # DEBUG: Verificar la página actual
            print(f"📄 Página actual: {self.driver.current_url}")
            print(f"📝 Título: {self.driver.title}")
            
            # Delegar el login al automation específico
            if hasattr(self.automation, 'login_automatico'):
                print("🔄 Usando método login_automatico específico...")
                resultado = self.automation.login_automatico(username, password)
            else:
                print("🔄 Usando método login genérico...")
                resultado = self._login_generico(username, password)
            
            if resultado:
                print("🎉 ¡Sesión iniciada automáticamente!")
                return True
            else:
                print("❌ Falló el inicio de sesión automático")
                print("💡 Usa forzar_login_manual() para reintentar")
                return False
                
        except Exception as e:
            print(f"❌ Error en inicio de sesión automático: {e}")
            return False
    
    def _login_generico(self, username, password):
        """Método de login genérico como fallback - ACTUALIZADO"""
        try:
            print("🔍 Buscando campos de login...")
            
            if self.plataforma == "cardmarket":
                # SELECTORES ACTUALIZADOS para CardMarket
                username_selectors = [
                    "input[name='username']",
                    "input[type='text']", 
                    "input[name='user[username]']"
                ]
                
                password_selectors = [
                    "input[type='password']",  # PRIMERO este
                    "input[name='password']",
                    "input[name='user[password]']"
                ]
                
                submit_selectors = [
                    "button[type='submit']",
                    "input[type='submit']",
                    "button[class*='btn-login']"
                ]
                
                # Probar diferentes selectores
                username_field = None
                for selector in username_selectors:
                    try:
                        username_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                        print(f"✅ Campo usuario encontrado: {selector}")
                        break
                    except:
                        continue
                
                password_field = None
                for selector in password_selectors:
                    try:
                        password_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                        print(f"✅ Campo contraseña encontrado: {selector}")
                        break
                    except:
                        continue
                
                submit_btn = None
                for selector in submit_selectors:
                    try:
                        submit_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                        print(f"✅ Botón enviar encontrado: {selector}")
                        break
                    except:
                        continue
                
                if not username_field or not password_field or not submit_btn:
                    print("❌ No se pudieron encontrar todos los campos")
                    return False
                    
            else:
                # Selectores para CardTrader (sin cambios)
                username_selector = "input[type='email']"
                password_selector = "input[type='password']"
                submit_selector = "input[type='submit'], button[type='submit']"
                
                username_field = self.driver.find_element(By.CSS_SELECTOR, username_selector)
                password_field = self.driver.find_element(By.CSS_SELECTOR, password_selector)
                submit_btn = self.driver.find_element(By.CSS_SELECTOR, submit_selector)
            
            print("⌨️  Rellenando campos...")
            
            # Usar JavaScript para mayor confiabilidad
            self.driver.execute_script("arguments[0].value = arguments[1];", username_field, username)
            self.driver.execute_script("arguments[0].value = arguments[1];", password_field, password)
            
            time.sleep(1)
            
            print("🖱️  Haciendo click en enviar...")
            self.driver.execute_script("arguments[0].click();", submit_btn)
            time.sleep(5)
            
            # Verificar si el login fue exitoso
            return self._verificar_login_exitoso()
            
        except Exception as e:
            print(f"❌ Error en login genérico: {e}")
            return False
    
    def _verificar_login_exitoso(self):
        """Verifica si el login fue exitoso - MEJORADA"""
        time.sleep(3)
        
        print("🔍 Verificando estado del login...")
        
        # Verificar si estamos en una página de error de login
        current_url = self.driver.current_url.lower()
        page_source = self.driver.page_source.lower()
        
        print(f"📄 URL actual: {current_url}")
        print(f"📝 Título página: {self.driver.title}")
        
        # Si estamos todavía en la página de login, verificar si hay errores específicos
        if "login" in current_url or "sign_in" in current_url:
            print("❌ Parece que el login falló - todavía en página de login")
            
            # Buscar mensajes de error específicos
            errores_especificos = [
                "incorrect", "invalid", "contraseña incorrecta", "usuario no encontrado"
            ]
            
            if any(error in page_source for error in errores_especificos):
                print("❌ Se detectó error específico de login")
                return False
            else:
                print("⚠️ En página de login pero sin errores específicos")
                return False
        
        # Si NO estamos en página de login, buscar indicadores positivos
        print("✅ No estamos en página de login - buscando indicadores positivos...")
        
        # Buscar indicadores de sesión activa
        indicadores_sesion = [
            "mi cuenta", "my account", "logout", "sign out", "cerrar sesión"
        ]
        
        for indicador in indicadores_sesion:
            if indicador in page_source:
                print(f"✅ Indicador de sesión encontrado: '{indicador}'")
                return True
        
        # Verificar por elementos específicos de CardMarket
        try:
            # Buscar elementos que indican sesión activa en CardMarket
            elementos_sesion = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/users/sign_out')]")
            if elementos_sesion:
                print("✅ Sesión activa detectada en CardMarket")
                return True
        except:
            pass
        
        # Si llegamos aquí y no estamos en login, asumimos éxito
        if "login" not in current_url and "sign_in" not in current_url:
            print("✅ No estamos en página de login - asumiendo éxito")
            return True
        
        print("⚠️ No se pudo verificar claramente el estado del login")
        return False

    def verificar_sesion_activa(self):
        """Verifica si hay una sesión activa"""
        if hasattr(self.automation, '_verificar_login_cardmarket_exitoso'):
            return self.automation._verificar_login_cardmarket_exitoso()
        else:
            return self._verificar_login_exitoso()

    def forzar_login_manual(self, parent_window=None):
        """Fuerza un login manual a través del diálogo"""
        try:
            if parent_window is None:
                # Crear una ventana temporal si no se proporciona una
                parent_window = tk.Tk()
                parent_window.withdraw()  # Ocultar la ventana principal temporal
            
            dialog = LoginDialog(parent_window, self.plataforma)
            resultado = dialog.show()
            
            if resultado:
                # Guardar credenciales si el usuario quiere recordarlas
                if resultado['remember']:
                    self.config_manager.set_credentials(
                        self.plataforma, 
                        resultado['username'], 
                        resultado['password']
                    )
                    print("✅ Credenciales guardadas")
                
                # Reintentar login con las nuevas credenciales
                return self._iniciar_sesion_automatica()
            
            return False
            
        except Exception as e:
            print(f"❌ Error en login manual: {e}")
            return False

    def buscar_desde_pagina_principal(self, nombre_carta):
        """Busca desde página principal con verificación de sesión"""
        # Verificar sesión primero
        if not self.verificar_sesion_activa():
            print("❌ No hay sesión activa. No se puede buscar.")
            print("💡 Usa forzar_login_manual() para iniciar sesión")
            return False
        
        return self.automation.buscar_desde_pagina_principal(nombre_carta)
    
    # El resto de los métodos permanecen igual...
    def seleccionar_carta_mas_barata(self, nombre_carta):
        return self.automation.seleccionar_carta_mas_barata(nombre_carta)
    
    def buscar_vendedores_con_zero_real(self, condiciones, cantidad_necesaria=1):
        return self.automation.buscar_vendedores_con_zero_real(condiciones, cantidad_necesaria)
    
    def cerrar_popups(self):
        return self.automation.cerrar_popups()
    
    def seleccionar_carta_con_reintentos(self, nombre_carta, condiciones, cantidad_necesaria=1):
        return self.automation.seleccionar_carta_con_reintentos(nombre_carta, condiciones, cantidad_necesaria)
    
    def _procesar_compra_con_cantidad(self, vendedores, cantidad_total, nombre_carta):
        return self.automation._procesar_compra_con_cantidad(vendedores, cantidad_total, nombre_carta)
    
    def agregar_al_carrito_confiable(self, vendedor):
        return self.automation.agregar_al_carrito_confiable(vendedor)
    
    def verificar_agregado_carrito(self):
        return self.automation.verificar_agregado_carrito()
    
    def mantener_abierto(self):
        return self.automation.mantener_abierto()
    
    def cerrar(self):
        return self.automation.cerrar()
    
    # NUEVO: Métodos para acceder a los vendedores seleccionados
    def obtener_vendedores_seleccionados(self):
        """Retorna la lista de vendedores seleccionados"""
        if hasattr(self.automation, 'vendedores_seleccionados'):
            return self.automation.vendedores_seleccionados
        return []
    
    def obtener_vendedores_unicos(self):
        """Retorna una lista de vendedores únicos"""
        if hasattr(self.automation, 'obtener_vendedores_unicos'):
            return self.automation.obtener_vendedores_unicos()
        return []
    
    def mostrar_resumen_vendedores(self):
        """Muestra un resumen de los vendedores seleccionados"""
        if hasattr(self.automation, '_mostrar_resumen_vendedores_guardados'):
            return self.automation._mostrar_resumen_vendedores_guardados()
        print("📋 No hay información de vendedores disponible")