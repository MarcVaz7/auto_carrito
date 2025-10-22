from cardtrader.cardtrader_automation import CardTraderAutomation
from cardmarket.cardmarket_automation import CardMarketAutomation

class CardAutomation:
    def __init__(self, plataforma="cardtrader"):
        self.plataforma = plataforma.lower()
        if self.plataforma == "cardmarket":
            self.automation = CardMarketAutomation()
            print("🌐 Plataforma: CardMarket seleccionada")
        else:
            self.automation = CardTraderAutomation()
            print("🌐 Plataforma: CardTrader seleccionada (por defecto)")
        
        # Delegar métodos al automation específico
        self.driver = self.automation.driver
        self.utils = self.automation.utils
    
    def buscar_desde_pagina_principal(self, nombre_carta):
        return self.automation.buscar_desde_pagina_principal(nombre_carta)
    
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