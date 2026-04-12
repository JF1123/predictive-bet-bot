import json

def simular_api_futbol():
    # Esta es la estructura exacta que te devolvería una API profesional como API-Sports.
    # Es un bloque de texto que parece un diccionario anidado.
    respuesta_servidor = """
    {
        "fecha_consulta": "2026-04-08",
        "liga": "Liga BetPlay Colombia",
        "partidos_hoy": [
            {
                "equipo_local": "Once Caldas",
                "equipo_visitante": "Millonarios",
                "estadisticas_historicas": {
                    "probabilidad_victoria_local": 45.5,
                    "probabilidad_empate": 25.0,
                    "probabilidad_victoria_visitante": 29.5
                },
                "cuotas_mercado": {
                    "1": 2.28,
                    "X": 3.20,
                    "2": 3.55
                }
            }
        ]
    }
    """
    # json.loads() convierte ese texto crudo en un "Diccionario" real de Python
    return json.loads(respuesta_servidor)

def ejecutar_recoleccion():
    print("📡 Conectando al servidor de datos deportivos...")
    
    # 1. Obtenemos los datos (AQUÍ ES DONDE EL BOT "LEE" INTERNET)
    datos = simular_api_futbol()
    print(f"✅ Conexión exitosa. Analizando la {datos['liga']}...\n")
    
    # 2. Filtramos solo la información que nos importa
    lista_partidos = datos["partidos_hoy"]
    
    for partido in lista_partidos:
        local = partido["equipo_local"]
        visitante = partido["equipo_visitante"]
        
        prob_local = partido["estadisticas_historicas"]["probabilidad_victoria_local"]
        cuota_local = partido["cuotas_mercado"]["1"]
        
        print(f"⚽ PARTIDO ENCONTRADO: {local} vs {visitante}")
        print(f"📊 El modelo histórico dice que {local} tiene un {prob_local}% de probabilidad de ganar.")
        print(f"💰 El mercado (BetPlay) está pagando una cuota de {cuota_local} por la victoria del local.\n")

if __name__ == "__main__":
    ejecutar_recoleccion()