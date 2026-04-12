import pandas as pd

def descargar_y_leer_datos():
    # Esta es la URL directa al archivo CSV de la Premier League 2023-2024
    # Como tu Codespace está en EE.UU., Coljuegos no puede bloquear esta petición.
    url = "https://www.football-data.co.uk/mmz4281/2324/E0.csv"
    
    print("☁️ Descargando datos desde los servidores en Reino Unido...")
    
    # pandas lee el archivo desde internet y lo convierte en una tabla instantáneamente
    df = pd.read_csv(url)
    
    print("✅ Datos descargados con éxito!")
    print(f"📊 Total de partidos históricos descargados: {len(df)}\n")
    
    print("--- PRIMEROS 5 PARTIDOS DEL DATASET ---")
    # Filtramos solo las columnas que nos importan para no saturar la pantalla:
    # HomeTeam (Local), AwayTeam (Visitante), FTHG (Goles Local), FTAG (Goles Visitante)
    # B365H, B365D, B365A (Cuotas históricas de Bet365 para 1, X, 2)
    columnas_clave = ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'B365H', 'B365D', 'B365A']
    
    # Imprimimos la tabla
    print(df[columnas_clave].head())

if __name__ == "__main__":
    descargar_y_leer_datos()