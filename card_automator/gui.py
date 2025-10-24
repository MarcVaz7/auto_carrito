import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import sys
import os
import re
from collections import Counter

# Añadir el directorio actual al path para importar los módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shared.multi_card_automator import MultiCardAutomator
from login_dialog import LoginDialog
from config_manager import ConfigManager

class CardAutomatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Card Automator - CardTrader & CardMarket")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Variable para controlar si el proceso está en ejecución
        self.running = False
        self.automator = None
        self.config_manager = ConfigManager()
        
        self.setup_ui()
        
        # ACTUALIZADO: Verificar configuración al inicializar
        self.verificar_configuracion_inicial()
    
    def verificar_configuracion_inicial(self):
        """Verifica la configuración al iniciar la aplicación"""
        try:
            plataforma = self.platform_var.get()
            
            if plataforma == "cardtrader":
                self.log_message(f"🌐 CardTrader: Modo invitado - no se requieren credenciales")
                self.update_status("CardTrader - Modo invitado")
            else:
                creds = self.config_manager.get_credentials(plataforma)
                if creds.get('username') and creds.get('password'):
                    self.log_message(f"✅ Credenciales encontradas para {plataforma.upper()}")
                    self.update_status(f"Credenciales configuradas para {plataforma.upper()}")
                else:
                    self.log_message(f"ℹ️ No hay credenciales guardadas para {plataforma.upper()}")
                    self.update_status(f"Configura credenciales para {plataforma.upper()}")
                
        except Exception as e:
            self.log_message(f"❌ Error al verificar configuración: {e}")
    
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, 
                               text="🚀 Card Automator - Multiplataforma", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Selector de plataforma
        platform_frame = ttk.Frame(main_frame)
        platform_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        ttk.Label(platform_frame, text="Plataforma:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        
        self.platform_var = tk.StringVar(value="cardtrader")
        
        def on_platform_change(*args):
            """Se ejecuta cuando cambia la plataforma"""
            self.verificar_configuracion_inicial()
        
        self.platform_var.trace('w', on_platform_change)
        
        ttk.Radiobutton(platform_frame, text="CardTrader", variable=self.platform_var, value="cardtrader").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(platform_frame, text="CardMarket", variable=self.platform_var, value="cardmarket").pack(side=tk.LEFT)
        
        # Botón de gestión de credenciales
        ttk.Button(platform_frame, text="🔐 Gestionar Credenciales", 
                  command=self.gestionar_credenciales).pack(side=tk.LEFT, padx=(20, 0))
        
        # ACTUALIZADO: Botón de verificar estado
        ttk.Button(platform_frame, text="🔍 Verificar Estado", 
                  command=self.verificar_estado_actual).pack(side=tk.LEFT, padx=(10, 0))
        
        # Instrucciones
        instructions = ttk.Label(main_frame, 
                                text="Ingresa los nombres de las cartas (uno por línea):",
                                font=("Arial", 10))
        instructions.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        
        # Info de limpieza automática
        cleanup_info = ttk.Label(main_frame, 
                                text="💡 Ejemplo: '2 Mountain' añadirá 2 Mountains. 'Sauron, The Dark Lord' se mantendrá como una sola carta.",
                                font=("Arial", 9),
                                foreground="blue",
                                wraplength=700)
        cleanup_info.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Área de texto para las cartas
        self.cards_text = scrolledtext.ScrolledText(main_frame, 
                                                   height=10, 
                                                   width=60,
                                                   font=("Consolas", 10))
        self.cards_text.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Frame para controles
        controls_frame = ttk.Frame(main_frame)
        controls_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Botón de inicio
        self.start_button = ttk.Button(controls_frame, 
                                      text="🚀 Iniciar Automatización", 
                                      command=self.start_automation)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón de detener
        self.stop_button = ttk.Button(controls_frame, 
                                     text="⏹️ Detener", 
                                     command=self.stop_automation,
                                     state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón de limpiar
        ttk.Button(controls_frame, 
                  text="🧹 Limpiar", 
                  command=self.clear_text).pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón de ejemplo
        ttk.Button(controls_frame, 
                  text="📋 Ejemplo", 
                  command=self.load_example).pack(side=tk.LEFT)
        
        # Área de logs
        log_label = ttk.Label(main_frame, text="Log de ejecución:", font=("Arial", 10, "bold"))
        log_label.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        
        self.log_text = scrolledtext.ScrolledText(main_frame, 
                                                 height=15, 
                                                 width=60,
                                                 font=("Consolas", 9),
                                                 state=tk.DISABLED)
        self.log_text.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Barra de progreso
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Status
        self.status_var = tk.StringVar(value="Listo para comenzar")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, font=("Arial", 9))
        status_label.grid(row=9, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
    
    def verificar_estado_actual(self):
        """Verifica el estado actual de la plataforma"""
        plataforma = self.platform_var.get()
        
        if plataforma == "cardtrader":
            self.log_message("🌐 CardTrader: Verificando estado...")
            self.update_status("Verificando CardTrader...")
            
            try:
                # Crear automator temporal para verificar estado
                automator_temp = MultiCardAutomator(plataforma=plataforma)
                
                self.log_message("✅ CardTrader configurado correctamente")
                self.log_message("💡 Modo invitado - no se requiere sesión activa")
                self.update_status("CardTrader - Listo (modo invitado)")
                
                messagebox.showinfo(
                    "CardTrader - Estado", 
                    "CardTrader está configurado correctamente.\n\n"
                    "Modo: Invitado\n"
                    "No se requiere iniciar sesión para buscar cartas.\n"
                    "El usuario iniciará sesión manualmente al pagar."
                )
                
                # Cerrar el automator temporal
                automator_temp.cerrar_todo()
                
            except Exception as e:
                self.log_message(f"❌ Error al verificar CardTrader: {e}")
                self.update_status("Error verificando CardTrader")
                messagebox.showerror("Error", f"No se pudo verificar CardTrader:\n{str(e)}")
        else:
            # Código existente para CardMarket
            creds = self.config_manager.get_credentials(plataforma)
            if not creds.get('username') or not creds.get('password'):
                messagebox.showinfo(
                    "Verificar Estado", 
                    f"No hay credenciales guardadas para {plataforma.upper()}.\n\n"
                    "Usa 'Gestionar Credenciales' para configurarlas."
                )
                return
            
            try:
                self.log_message(f"🔍 Verificando estado en {plataforma.upper()}...")
                self.update_status("Verificando estado...")
                
                # Crear automator temporal para verificar sesión
                automator_temp = MultiCardAutomator(plataforma=plataforma)
                
                if automator_temp.verificar_sesion():
                    self.log_message("✅ Sesión activa verificada correctamente")
                    self.update_status("Sesión activa")
                    messagebox.showinfo("Verificación de Estado", "✅ Sesión activa verificada correctamente")
                else:
                    self.log_message("❌ No hay sesión activa")
                    self.update_status("No hay sesión activa")
                    messagebox.showwarning("Verificación de Estado", 
                                        "❌ No hay una sesión activa.\n\n"
                                        "Inicia la automatización para forzar el login.")
                
                # Cerrar el automator temporal
                automator_temp.cerrar_todo()
                
            except Exception as e:
                self.log_message(f"❌ Error al verificar estado: {e}")
                self.update_status("Error verificando estado")
                messagebox.showerror("Error", f"No se pudo verificar el estado:\n{str(e)}")
    
    def gestionar_credenciales(self):
        """Gestiona las credenciales guardadas"""
        plataforma = self.platform_var.get()
        
        if plataforma == "cardtrader":
            messagebox.showinfo(
                "CardTrader - Información",
                "CardTrader no requiere credenciales guardadas.\n\n"
                "La plataforma funciona en modo invitado.\n"
                "Las cartas se agregan al carrito sin necesidad de iniciar sesión.\n"
                "El usuario inicia sesión manualmente al finalizar la compra."
            )
            return
        
        creds = self.config_manager.get_credentials(plataforma)
        
        if creds.get('username'):
            respuesta = messagebox.askyesno(
                "Gestionar Credenciales",
                f"¿Quieres eliminar las credenciales guardadas para {plataforma.upper()}?\n\nUsuario: {creds['username']}"
            )
            if respuesta:
                if self.config_manager.clear_credentials(plataforma):
                    messagebox.showinfo("Éxito", "Credenciales eliminadas correctamente.")
                    self.log_message(f"🗑️ Credenciales eliminadas para {plataforma.upper()}")
                    self.update_status("Credenciales eliminadas")
                else:
                    messagebox.showerror("Error", "No se pudieron eliminar las credenciales.")
        else:
            # No hay credenciales, ofrecer configurarlas
            respuesta = messagebox.askyesno(
                "Configurar Credenciales",
                f"No hay credenciales guardadas para {plataforma.upper()}.\n\n¿Quieres configurarlas ahora?"
            )
            if respuesta:
                self.configurar_credenciales(plataforma)
    
    def configurar_credenciales(self, plataforma):
        """Configura las credenciales para una plataforma"""
        dialog = LoginDialog(self.root, plataforma)
        resultado = dialog.show()
        
        if resultado:
            if resultado['remember']:
                self.config_manager.set_credentials(plataforma, 
                                                  resultado['username'], 
                                                  resultado['password'])
                self.log_message(f"🔐 Credenciales guardadas para {plataforma.upper()}")
                self.update_status(f"Credenciales guardadas para {plataforma.upper()}")
                messagebox.showinfo("Éxito", "Credenciales guardadas correctamente.")
            else:
                self.log_message(f"🔐 Credenciales configuradas (no guardadas) para {plataforma.upper()}")
                self.update_status(f"Credenciales configuradas para {plataforma.upper()}")
    
    def procesar_linea_carta(self, linea):
        """
        Procesa una línea de texto que puede contener:
        - Número de copias (ej: "2 Mountain")
        - Nombre con coma (ej: "Sauron, The Dark Lord")
        
        Retorna: lista de nombres de cartas (puede tener múltiples copias)
        """
        if not linea.strip():
            return []
        
        linea = linea.strip()
        
        # Buscar número al inicio (ej: "2 Mountain", "3x Forest", "1 Sol Ring")
        patron_numero = r'^(\d+)\s*(?:x\s*)?(.+)$'
        match = re.match(patron_numero, linea)
        
        if match:
            cantidad = int(match.group(1))
            nombre_carta = match.group(2).strip()
            
            # Si la carta tiene coma en el nombre (ej: "Sauron, The Dark Lord"),
            # mantenerla como una sola carta reemplazando la coma por espacio
            if ',' in nombre_carta:
                nombre_carta = nombre_carta.replace(',', ' ')
            
            # Limpiar espacios múltiples
            nombre_carta = re.sub(r'\s+', ' ', nombre_carta).strip()
            
            # Capitalizar palabras (excepto palabras pequeñas)
            palabras = nombre_carta.split()
            palabras_capitalizadas = []
            
            for palabra in palabras:
                if len(palabra) > 2:  # Solo capitalizar palabras de 3+ letras
                    palabras_capitalizadas.append(palabra.capitalize())
                else:
                    palabras_capitalizadas.append(palabra.lower())
            
            nombre_carta = ' '.join(palabras_capitalizadas)
            
            # Retornar múltiples copias si la cantidad es > 1
            return [nombre_carta] * cantidad
        
        else:
            # No hay número, procesar como carta única
            nombre_carta = linea
            
            # Manejar comas en el nombre
            if ',' in nombre_carta:
                nombre_carta = nombre_carta.replace(',', ' ')
            
            # Limpiar espacios múltiples
            nombre_carta = re.sub(r'\s+', ' ', nombre_carta).strip()
            
            # Capitalizar palabras
            palabras = nombre_carta.split()
            palabras_capitalizadas = []
            
            for palabra in palabras:
                if len(palabra) > 2:
                    palabras_capitalizadas.append(palabra.capitalize())
                else:
                    palabras_capitalizadas.append(palabra.lower())
            
            nombre_carta = ' '.join(palabras_capitalizadas)
            
            return [nombre_carta]
    
    def log_message(self, message):
        """Añade un mensaje al área de logs"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def update_status(self, message):
        """Actualiza el mensaje de estado"""
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def clear_text(self):
        """Limpia el área de texto"""
        self.cards_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.update_status("Listo para comenzar")
    
    def load_example(self):
        """Carga un ejemplo de cartas con diferentes formatos"""
        example_cards = """1 Command Tower
2 Mountain
3 Forest
1 Sol Ring
2 Sauron, The Dark Lord
1 Arcane Signet
4 Island
2 Swamp
1 Plains
3 Cultivate"""
        
        self.cards_text.delete(1.0, tk.END)
        self.cards_text.insert(1.0, example_cards)
    
    def get_cards_list(self):
        """Obtiene y procesa la lista de cartas del texto"""
        text = self.cards_text.get(1.0, tk.END).strip()
        if not text:
            return []
        
        # Procesar línea por línea
        todas_las_cartas = []
        
        for linea in text.split('\n'):
            linea = linea.strip()
            if linea:
                cartas_de_esta_linea = self.procesar_linea_carta(linea)
                todas_las_cartas.extend(cartas_de_esta_linea)
        
        return todas_las_cartas
    
    def verificar_configuracion(self, plataforma):
        """Verifica y gestiona la configuración para la plataforma"""
        if plataforma == "cardtrader":
            # CardTrader no requiere credenciales
            self.log_message("🌐 CardTrader: No se requieren credenciales - modo invitado")
            return True
        else:
            # CardMarket requiere credenciales
            creds = self.config_manager.get_credentials(plataforma)
            
            if not creds.get('username') or not creds.get('password'):
                respuesta = messagebox.askyesno(
                    "Credenciales Requeridas",
                    f"No hay credenciales guardadas para {plataforma.upper()}.\n\n¿Quieres configurarlas ahora?"
                )
                
                if not respuesta:
                    return False
                
                dialog = LoginDialog(self.root, plataforma)
                resultado = dialog.show()
                
                if not resultado:
                    return False
                
                # Guardar credenciales si el usuario quiere
                if resultado['remember']:
                    self.config_manager.set_credentials(plataforma, 
                                                      resultado['username'], 
                                                      resultado['password'])
                    self.log_message(f"🔐 Credenciales guardadas para {plataforma.upper()}")
                else:
                    self.log_message(f"🔐 Credenciales configuradas para {plataforma.upper()}")
            
            return True
    
    def start_automation(self):
        """Inicia la automatización en un hilo separado"""
        cards = self.get_cards_list()
        
        if not cards:
            messagebox.showwarning("Advertencia", "Por favor, ingresa al menos una carta.")
            return
        
        plataforma = self.platform_var.get()
        
        # VERIFICAR CONFIGURACIÓN PRIMERO
        if not self.verificar_configuracion(plataforma):
            self.log_message("❌ Automatización cancelada: configuración requerida")
            return
        
        self.log_message(f"🌐 Plataforma seleccionada: {plataforma.upper()}")
        
        # Mostrar información específica por plataforma
        if plataforma == "cardtrader":
            self.log_message("💡 CardTrader: Modo invitado activado")
            self.log_message("   - No se requiere iniciar sesión")
            self.log_message("   - Las cartas se agregan al carrito como invitado")
            self.log_message("   - Inicia sesión manualmente al pagar")
        else:
            self.log_message("💡 CardMarket: Modo con sesión activa")
            self.log_message("   - Se requiere sesión activa")
            self.log_message("   - Las cartas se agregan a tu cuenta")
        
        # Mostrar transformación en el log
        self.log_message("🧹 Procesando lista de cartas...")
        self.log_message(f"📋 Se procesarán {len(cards)} cartas en total")
        
        # Contar cartas únicas para mostrar info
        from collections import Counter
        contador = Counter(cards)
        if len(contador) < len(cards):
            self.log_message("📊 Desglose:")
            for carta, cantidad in contador.items():
                if cantidad > 1:
                    self.log_message(f"   - {carta} (x{cantidad})")
                else:
                    self.log_message(f"   - {carta}")
        
        # Deshabilitar controles
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.cards_text.config(state=tk.DISABLED)
        self.running = True
        
        # Limpiar logs
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        # Iniciar barra de progreso
        self.progress.start()
        
        # Actualizar estado
        self.update_status(f"Procesando {len(cards)} cartas en {plataforma.upper()}...")
        
        # Ejecutar en un hilo separado para no bloquear la GUI
        thread = threading.Thread(target=self.run_automation, args=(cards, plataforma))
        thread.daemon = True
        thread.start()
    
    def run_automation(self, cards, plataforma):
        """Ejecuta la automatización (en hilo separado)"""
        try:
            # El MultiCardAutomator ahora maneja la configuración automáticamente
            self.automator = MultiCardAutomator(plataforma=plataforma)
            
            # Redirigir print a nuestro logger
            import builtins
            original_print = builtins.print
            
            def custom_print(*args, **kwargs):
                message = " ".join(str(arg) for arg in args)
                self.root.after(0, lambda: self.log_message(message))
                # También mantener el print original para la consola
                original_print(*args, **kwargs)
            
            builtins.print = custom_print
            
            # Procesar cartas
            self.log_message("=" * 60)
            self.log_message(f"🚀 INICIANDO AUTOMATIZACIÓN {plataforma.upper()}")
            self.log_message("=" * 60)
            self.log_message(f"📋 Cartas a procesar: {len(cards)}")
            self.log_message("✅ Filtros: Vendedores UE + Cartas Inglés + SOLO NM + Zero")
            self.log_message("")
            
            exitos, fallos = self.automator.procesar_lista_cartas(cards)
            
            # Restaurar print original
            builtins.print = original_print
            
            # Mostrar resultados
            self.root.after(0, self.automation_completed, exitos, fallos, cards, plataforma)
            
        except Exception as e:
            self.root.after(0, self.automation_failed, str(e))
    
    def automation_completed(self, exitos, fallos, cards, plataforma):
        """Se llama cuando la automatización se completa"""
        self.progress.stop()
        self.running = False
        
        # Habilitar controles
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.cards_text.config(state=tk.NORMAL)
        
        # Mostrar resumen
        self.log_message("")
        self.log_message("=" * 60)
        self.log_message("📊 RESUMEN FINAL")
        self.log_message("=" * 60)
        self.log_message(f"🌐 Plataforma: {plataforma.upper()}")
        self.log_message(f"✅ Se han añadido {exitos} cartas")
        
        if fallos > 0:
            self.log_message(f"❌ Han fallado {fallos} cartas")
        else:
            self.log_message("🎉 ¡Todas las cartas se añadieron correctamente!")
        
        self.update_status(f"Completado: {exitos}/{len(cards)} cartas añadidas en {plataforma.upper()}")
        
        # Mostrar mensaje de finalización
        messagebox.showinfo("Completado", 
                           f"Automatización completada en {plataforma.upper()}:\n"
                           f"✅ {exitos} cartas añadidas\n"
                           f"❌ {fallos} cartas falladas")
    
    def automation_failed(self, error_message):
        """Se llama cuando la automatización falla"""
        self.progress.stop()
        self.running = False
        
        # Habilitar controles
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.cards_text.config(state=tk.NORMAL)
        
        self.log_message(f"❌ ERROR CRÍTICO: {error_message}")
        self.update_status("Error en la automatización")
        
        messagebox.showerror("Error", f"Ocurrió un error durante la automatización:\n{error_message}")
    
    def stop_automation(self):
        """Detiene la automatización"""
        if self.running and self.automator:
            self.running = False
            self.update_status("Deteniendo...")
            self.log_message("⏹️ Deteniendo automatización...")
            
            try:
                self.automator.cerrar_todo()
            except:
                pass
            
            self.progress.stop()
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.cards_text.config(state=tk.NORMAL)
            self.update_status("Detenido por el usuario")