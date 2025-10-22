import json
import os
import getpass

class ConfigManager:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self):
        """Carga la configuración desde el archivo"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_config(self):
        """Guarda la configuración en el archivo"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except:
            return False
    
    def get_credentials(self, platform):
        """Obtiene las credenciales para una plataforma"""
        return self.config.get(platform, {})
    
    def set_credentials(self, platform, username, password):
        """Guarda las credenciales para una plataforma"""
        if platform not in self.config:
            self.config[platform] = {}
        
        self.config[platform]['username'] = username
        # En una aplicación real, deberías encriptar la contraseña
        self.config[platform]['password'] = password
        return self.save_config()
    
    def has_credentials(self, platform):
        """Verifica si existen credenciales para una plataforma"""
        creds = self.get_credentials(platform)
        return bool(creds.get('username')) and bool(creds.get('password'))
    
    def clear_credentials(self, platform):
        """Elimina las credenciales de una plataforma"""
        if platform in self.config:
            del self.config[platform]
            return self.save_config()
        return True