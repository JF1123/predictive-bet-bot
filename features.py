import pandas as pd

def generar_rachas_historicas():
    print("⚙️ Procesando la Ingeniería de Características (Feature Engineering)...")
    
    # 1. Cargar datos base
    url = "https://www.football-data.co.uk/mmz4281/2324/E0.csv"
    df = pd.read_csv(url)
    
    # Asegurarnos de que las fechas estén en orden cronológico (vital para promedios móviles)
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
    df = df.sort_values('Date')
    
    # 2. LA MATEMÁTICA DE LAS RACHAS (Rolling Averages)
    # Calculamos el promedio de los últimos 3 partidos jugando de local para el HomeTeam
    # El shift(1) es nuestra protección contra la Fuga de Datos (no ver el futuro)
    
    # Poder Ofensivo Local
    df['Local_Goles_Anotados_Prom'] = df.groupby('HomeTeam')['FTHG'].transform(lambda x: x.shift(1).rolling(3, min_periods=1).mean())
    df['Local_Tiros_Arco_Prom'] = df.groupby('HomeTeam')['HST'].transform(lambda x: x.shift(1).rolling(3, min_periods=1).mean())
    
    # Poder Ofensivo Visitante
    df['Visit_Goles_Anotados_Prom'] = df.groupby('AwayTeam')['FTAG'].transform(lambda x: x.shift(1).rolling(3, min_periods=1).mean())
    df['Visit_Tiros_Arco_Prom'] = df.groupby('AwayTeam')['AST'].transform(lambda x: x.shift(1).rolling(3, min_periods=1).mean())
    
    # Vulnerabilidad Defensiva (Goles recibidos)
    df['Local_Goles_Recibidos_Prom'] = df.groupby('HomeTeam')['FTAG'].transform(lambda x: x.shift(1).rolling(3, min_periods=1).mean())
    df['Visit_Goles_Recibidos_Prom'] = df.groupby('AwayTeam')['FTHG'].transform(lambda x: x.shift(1).rolling(3, min_periods=1).mean())
    
    # 3. LIMPIEZA
    # Las primeras jornadas (fechas 1 y 2) tendrán datos vacíos (NaN) porque no hay historial previo.
    # En Machine Learning, la basura matemática arruina el modelo, así que borramos esos partidos.
    df = df.dropna(subset=['Local_Goles_Anotados_Prom'])
    
    print("✅ ¡Nuevos datos generados matemáticamente!")
    print(f"Partidos listos para entrenar: {len(df)}\n")
    
    # Mostramos un ejemplo de cómo se ve el "nuevo" set de datos
    columnas_ver = ['Date', 'HomeTeam', 'Local_Goles_Anotados_Prom', 'Local_Tiros_Arco_Prom']
    
    print("--- HISTORIAL DE RACHAS DEL EQUIPO LOCAL (Ejemplo) ---")
    print(df[columnas_ver].head(10))
    
    return df

if __name__ == "__main__":
    generar_rachas_historicas()