import PyInstaller.__main__
import os
import sys

def build_executable():
    """Crea el ejecutable usando PyInstaller con la nueva estructura"""
    
    print("🚀 Iniciando construcción del ejecutable...")
    
    # Verificar que todos los archivos necesarios existen
    required_files = [
        'main.py',                    # Archivo principal nuevo
        'gui.py',
        'CommanderCart.py',
        'config_manager.py',
        'login_dialog.py', 
        'utils.py',
        # Verificar que existen las carpetas de módulos
        'cardtrader/__init__.py',
        'cardtrader/cardtrader_automation.py',
        'cardtrader/cardtrader_selector.py',
        'cardtrader/cardtrader_finder.py',
        'cardmarket/__init__.py',
        'cardmarket/cardmarket_automation.py',
        'cardmarket/cardmarket_selector.py',
        'cardmarket/cardmarket_finder.py',
        'shared/__init__.py',
        'shared/base_automation.py',
        'shared/multi_card_automator.py',
        'shared/base_platform.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Archivos faltantes:")
        for file in missing_files:
            print(f"   - {file}")
        print("\n💡 Asegúrate de que todos los archivos estén en la estructura correcta.")
        return
    
    print("✅ Todos los archivos necesarios encontrados")
    
    # Opciones de PyInstaller
    pyinstaller_args = [
        'main.py',                    # Archivo principal cambiado
        '--name=CardAutomator',       # Nuevo nombre más genérico
        '--onefile',                  # Un solo archivo ejecutable
        '--windowed',                 # Sin ventana de consola
        '--clean',                    # Limpiar build anterior
        '--noconfirm',                # No preguntar para sobrescribir
        '--add-data=cardtrader;cardtrader',      # Incluir módulo cardtrader
        '--add-data=cardmarket;cardmarket',      # Incluir módulo cardmarket  
        '--add-data=shared;shared',              # Incluir módulo shared
        '--hidden-import=cardtrader.cardtrader_automation',
        '--hidden-import=cardtrader.cardtrader_selector',
        '--hidden-import=cardtrader.cardtrader_finder',
        '--hidden-import=cardmarket.cardmarket_automation',
        '--hidden-import=cardmarket.cardmarket_selector',
        '--hidden-import=cardmarket.cardmarket_finder',
        '--hidden-import=shared.base_automation',
        '--hidden-import=shared.multi_card_automator',
        '--hidden-import=shared.base_platform',
        '--hidden-import=config_manager',
        '--hidden-import=login_dialog',
        '--hidden-import=utils'
    ]
    
    print("📦 Módulos que se incluirán en el ejecutable:")
    print("   - cardtrader (CardTrader automation)")
    print("   - cardmarket (CardMarket automation)") 
    print("   - shared (componentes compartidos)")
    print("   - GUI y utilidades")
    
    print("\n⚙️ Configuración:")
    print("   - Modo: OneFile (un solo ejecutable)")
    print("   - Interfaz: Windowed (sin consola)")
    print("   - Nombre: CardAutomator.exe")
    print("   - Plataformas: CardTrader + CardMarket")
    
    try:
        print("\n🔨 Construyendo ejecutable... (esto puede tomar varios minutos)")
        PyInstaller.__main__.run(pyinstaller_args)
        
        print("\n✅ ¡Ejecutable creado exitosamente!")
        print("📁 El ejecutable está en la carpeta 'dist/CardAutomator.exe'")
        print("\n🎉 ¡Ya puedes compartir CardAutomator.exe!")
        print("   Ahora soporta ambas plataformas: CardTrader y CardMarket")
        
    except Exception as e:
        print(f"\n❌ Error creando el ejecutable: {e}")
        print("💡 Posibles soluciones:")
        print("   - Ejecuta como administrador")
        print("   - Cierra otros programas")
        print("   - Verifica que tienes suficiente espacio en disco")
        print("   - Asegúrate de que todos los módulos estén en su lugar")

if __name__ == "__main__":
    build_executable()