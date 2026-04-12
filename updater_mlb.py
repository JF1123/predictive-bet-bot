import statsapi
import pandas as pd
from datetime import datetime, timedelta
import os
import subprocess

# Diccionario Inverso: MLB Stats API -> Código de 3 letras de Retrosheet
MAPEO_INVERSO = {
    'Arizona Diamondbacks': 'ARI', 'Atlanta Braves': 'ATL', 'Baltimore Orioles': 'BAL',
    'Boston Red Sox': 'BOS', 'Chicago Cubs': 'CHN', 'Chicago White Sox': 'CHA',
    'Cincinnati Reds': 'CIN', 'Cleveland Guardians': 'CLE', 'Colorado Rockies': 'COL',
    'Detroit Tigers': 'DET', 'Houston Astros': 'HOU', 'Kansas City Royals': 'KCA',
    'Los Angeles Angels': 'ANA', 'Los Angeles Dodgers': 'LAN', 'Miami Marlins': 'MIA',
    'Milwaukee Brewers': 'MIL', 'Minnesota Twins': 'MIN', 'New York Mets': 'NYN',
    'New York Yankees': 'NYA', 'Oakland Athletics': 'OAK', 'Philadelphia Phillies': 'PHI',
    'Pittsburgh Pirates': 'PIT', 'San Diego Padres': 'SDN', 'San Francisco Giants': 'SFN',
    'Seattle Mariners': 'SEA', 'St. Louis Cardinals': 'SLN', 'Tampa Bay Rays': 'TBA',
    'Texas Rangers': 'TEX', 'Toronto Blue Jays': 'TOR', 'Washington Nationals': 'WAS'
}

def actualizar_cerebro_diario():
    # Calcular la fecha de ayer
    ayer = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    print(f"📡 Escaneando resultados de la MLB del {ayer}...")

    # Extraer partidos del calendario oficial
    try:
        juegos = statsapi.schedule(date=ayer)
    except Exception as e:
        print(f"❌ Error al conectar con MLB-StatsAPI: {e}")
        return

    if not juegos:
        print("⚾ No hubo partidos ayer (o es temporada baja). El Cerebro se mantiene intacto.")
        return

    nuevos_datos = []
    
    for j in juegos:
        if j['status'] != 'Final':
            continue # Solo nos importan los partidos que ya terminaron

        visita = MAPEO_INVERSO.get(j['away_name'], 'UNK')
        local = MAPEO_INVERSO.get(j['home_name'], 'UNK')
        
        # Extraemos carreras
        carreras_v = j.get('away_score', 0)
        carreras_l = j.get('home_score', 0)
        
        # Extraemos los nombres de los pitchers que abrieron/ganaron para trackear su efectividad
        pitcher_v = j.get('away_probable_pitcher', 'Desconocido')
        pitcher_l = j.get('home_probable_pitcher', 'Desconocido')

        fila = {
            'Fecha': datetime.strptime(ayer, '%Y-%m-%d').strftime('%Y-%m-%d'),
            'Visita': visita,
            'Local': local,
            'Carreras_Visita': carreras_v,
            'Carreras_Local': carreras_l,
            'Hits_Visita': 0, # Variable obsoleta para el V2, rellenamos con 0
            'HR_Visita': 0,   # Variable obsoleta para el V2, rellenamos con 0
            'Hits_Local': 0,  # Variable obsoleta para el V2, rellenamos con 0
            'HR_Local': 0,    # Variable obsoleta para el V2, rellenamos con 0
            'Pitcher_Visita': pitcher_v,
            'Pitcher_Local': pitcher_l,
            'Gana_Local': 1 if carreras_l > carreras_v else 0
        }
        nuevos_datos.append(fila)

    if nuevos_datos:
        archivo = 'mlb_historico.csv'
        if os.path.exists(archivo):
            df_historico = pd.read_csv(archivo)
            df_nuevos = pd.DataFrame(nuevos_datos)
            
            # Concatenar y asegurar que no haya duplicados si el script se corre por accidente dos veces
            df_actualizado = pd.concat([df_historico, df_nuevos], ignore_index=True)
            df_actualizado = df_actualizado.drop_duplicates(subset=['Fecha', 'Visita', 'Local'])
            
            # Sobrescribir la base de datos maestra
            df_actualizado.to_csv(archivo, index=False)
            print(f"✅ ¡Éxito! Se añadieron {len(df_nuevos)} partidos al dataset.")
            
            # MAGIA MLOps: Mandar a reentrenar el modelo automáticamente desde aquí
            print("⚙️ Inyectando nuevos datos y regenerando los pesos del XGBoost...")
            subprocess.run(["python", "train_mlb.py"])
        else:
            print(f"❌ No se encontró la base maestra {archivo}.")
    else:
        print("⚾ No se encontraron resultados procesables de ayer.")

if __name__ == "__main__":
    actualizar_cerebro_diario()