import PyInstaller.__main__
import os
import sys

def build_executable():
    """Crea el ejecutable usando PyInstaller"""
    
    print("🚀 Iniciando construcción del ejecutable...")
    
    # Verificar que todos los archivos necesarios existen
    required_files = [
        'cardtrader_gui.py',
        'ListCart.py', 
        'CommanderCart.py',
        'card_selector.py',
        'seller_finder.py',
        'utils.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Archivos faltantes:")
        for file in missing_files:
            print(f"   - {file}")
        print("\n💡 Asegúrate de que todos los archivos estén en la misma carpeta.")
        return
    
    print("✅ Todos los archivos necesarios encontrados")
    
    # Opciones de PyInstaller
    pyinstaller_args = [
        'cardtrader_gui.py',           # Archivo principal
        '--name=CardTraderAutomator',  # Nombre del ejecutable
        '--onefile',                   # Un solo archivo ejecutable
        '--windowed',                  # Sin ventana de consola
        '--clean',                     # Limpiar build anterior
        '--noconfirm',                 # No preguntar para sobrescribir
    ]
    
    print("📦 Archivos que se incluirán en el ejecutable:")
    for file in required_files:
        print(f"   - {file}")
    
    print("\n⚙️ Configuración:")
    print("   - Modo: OneFile (un solo ejecutable)")
    print("   - Interfaz: Windowed (sin consola)")
    print("   - Nombre: CardTraderAutomator.exe")
    
    try:
        print("\n🔨 Construyendo ejecutable... (esto puede tomar varios minutos)")
        PyInstaller.__main__.run(pyinstaller_args)
        
        print("\n✅ ¡Ejecutable creado exitosamente!")
        print("📁 El ejecutable está en la carpeta 'dist/CardTraderAutomator.exe'")
        print("\n🎉 ¡Ya puedes compartir CardTraderAutomator.exe con tus amigos!")
        
    except Exception as e:
        print(f"\n❌ Error creando el ejecutable: {e}")
        print("💡 Posibles soluciones:")
        print("   - Ejecuta como administrador")
        print("   - Cierra otros programas")
        print("   - Verifica que tienes suficiente espacio en disco")

if __name__ == "__main__":
    build_executable()