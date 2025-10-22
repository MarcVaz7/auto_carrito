import tkinter as tk
from tkinter import ttk, messagebox
import getpass

class LoginDialog:
    def __init__(self, parent, platform):
        self.parent = parent
        self.platform = platform
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Iniciar sesión - {platform.upper()}")
        self.dialog.geometry("400x200")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrar en la pantalla
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")
        
        self.setup_ui()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, 
                               text=f"Iniciar sesión en {self.platform.upper()}",
                               font=("Arial", 12, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Campo usuario
        ttk.Label(main_frame, text="Usuario:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(main_frame, textvariable=self.username_var, width=30)
        self.username_entry.grid(row=1, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
        
        # Campo contraseña
        ttk.Label(main_frame, text="Contraseña:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(main_frame, textvariable=self.password_var, 
                                       show="•", width=30)
        self.password_entry.grid(row=2, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
        
        # Checkbox recordar
        self.remember_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(main_frame, text="Recordar credenciales", 
                       variable=self.remember_var).grid(row=3, column=0, columnspan=2, 
                                                       sticky=tk.W, pady=10)
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(button_frame, text="Iniciar sesión", 
                  command=self.ok).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancelar", 
                  command=self.cancel).pack(side=tk.LEFT)
        
        # Configurar grid
        main_frame.columnconfigure(1, weight=1)
        
        # Enfocar el campo de usuario
        self.username_entry.focus()
        
        # Bind Enter key
        self.dialog.bind('<Return>', lambda e: self.ok())
    
    def ok(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        if not username or not password:
            messagebox.showwarning("Advertencia", 
                                 "Por favor, ingresa tanto usuario como contraseña.")
            return
        
        self.result = {
            'username': username,
            'password': password,
            'remember': self.remember_var.get()
        }
        self.dialog.destroy()
    
    def cancel(self):
        self.result = None
        self.dialog.destroy()
    
    def show(self):
        self.dialog.wait_window()
        return self.result