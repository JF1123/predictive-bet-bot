import requests
import pandas as pd
import joblib
import warnings
import json
import os
from datetime import datetime, timedelta

warnings.filterwarnings('ignore')

# --- CONFIGURACIÓN QUANT ---
API_KEY = '059df6f2341b819b810c4fcab8de323e' 
DEPORTE = 'baseball_mlb' 
MERCADO = 'h2h' 
REGION = 'us' # Las casas de EE.UU. tienen la mayor liquidez en MLB
ARCHIVO_CACHE = 'cache_mlb.json'
HORAS_VIGENCIA = 12
CAPITAL_TOTAL = 1000.00 

# Diccionario traductor: The Odds API -> Retrosheet
MAPEO_EQUIPOS = {
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

def calcular_kelly(probabilidad_ia, cuota, bankroll):
    p = probabilidad_ia / 100.0 
    fraccion_kelly = ((p * cuota) - 1) / (cuota - 1)
    
    # Usamos Cuarto de Kelly (Quarter-Kelly) para MLB, es más seguro a largo plazo
    fraccion_segura = fraccion_kelly * 0.25 
    
    # KELLY CAP: Nunca apostar más del 5% del bankroll en un solo juego
    if fraccion_segura > 0.05:
        fraccion_segura = 0.05
        
    if fraccion_segura <= 0: return 0.0
    
    # Redondeamos a 2 decimales limpios
    return round(bankroll * fraccion_segura, 2)

def cargar_historia_mlb():
    if not os.path.exists('mlb_historico.csv'):
        print("❌ Error: Falta 'mlb_historico.csv'.")
        return None
    return pd.read_csv('mlb_historico.csv')

def obtener_stats_equipo(equipo_api, df):
    codigo_retro = MAPEO_EQUIPOS.get(equipo_api)
    if not codigo_retro or df is None:
        return {'Ofensiva': 4.0, 'Defensa': 4.0} 
        
    carreras_anotadas = pd.concat([
        df[df['Local'] == codigo_retro]['Carreras_Local'],
        df[df['Visita'] == codigo_retro]['Carreras_Visita']
    ])
    
    carreras_permitidas = pd.concat([
        df[df['Local'] == codigo_retro]['Carreras_Visita'],
        df[df['Visita'] == codigo_retro]['Carreras_Local']
    ])
    
    ofensiva = carreras_anotadas.mean() if not carreras_anotadas.empty else 4.0
    defensa = carreras_permitidas.mean() if not carreras_permitidas.empty else 4.0
    
    return {'Ofensiva': round(ofensiva, 3), 'Defensa': round(defensa, 3)}

def obtener_datos_api():
    if os.path.exists(ARCHIVO_CACHE):
        tiempo_modificacion = datetime.fromtimestamp(os.path.getmtime(ARCHIVO_CACHE))
        if datetime.now() - tiempo_modificacion < timedelta(hours=HORAS_VIGENCIA):
            print("📦 Leyendo datos MLB desde el Caché local...")
            with open(ARCHIVO_CACHE, 'r') as f:
                return json.load(f)

    print("🌐 Consultando The Odds API para MLB...")
    url = f'https://api.the-odds-api.com/v4/sports/{DEPORTE}/odds/?apiKey={API_KEY}&regions={REGION}&markets={MERCADO}'
    respuesta = requests.get(url)
    
    if respuesta.status_code == 200:
        datos = respuesta.json()
        with open(ARCHIVO_CACHE, 'w') as f:
            json.dump(datos, f)
        return datos
    return None

def escanear_mercado_mlb():
    try:
        modelo = joblib.load('oraculo_mlb_xgboost.pkl')
    except:
        print("❌ Error: No se encontró 'oraculo_mlb_xgboost.pkl'.")
        return

    df_historico = cargar_historia_mlb()
    partidos = obtener_datos_api()
    
    if not partidos:
        print("⚾ No hay partidos de MLB programados o la API falló.")
        return

    print(f"\n💵 CAPITAL DISPONIBLE: ${CAPITAL_TOTAL} USD")
    print("🔍 Escaneando MLB con Inteligencia Cuantitativa...\n")
    print("=" * 60)
    
    for partido in partidos[:5]: # Escanea los primeros 5 partidos
        equipo_local = partido['home_team']
        equipo_visita = partido['away_team']
        
        if not partido['bookmakers']: continue
            
        # Tomamos la primera casa de apuestas disponible en US (ej. DraftKings, FanDuel, Bovada)
        casa_apuestas = partido['bookmakers'][0]['title']
        cuotas = partido['bookmakers'][0]['markets'][0]['outcomes']
        
        cuota_L = cuota_V = 0.0
        for opcion in cuotas:
            if opcion['name'] == equipo_local: cuota_L = opcion['price']
            elif opcion['name'] == equipo_visita: cuota_V = opcion['price']
            
        stats_local = obtener_stats_equipo(equipo_local, df_historico)
        stats_visita = obtener_stats_equipo(equipo_visita, df_historico)
        
        datos_prediccion = {
            'Fuerza_Ofensiva_Local': stats_local['Ofensiva'],
            'Fuerza_Ofensiva_Visita': stats_visita['Ofensiva'],
            'Defensa_Local': stats_local['Defensa'],
            'Defensa_Visita': stats_visita['Defensa']
        }
        
        df_partido = pd.DataFrame([datos_prediccion])
        
        # XGBoost devuelve [Prob_Gana_Visita(0), Prob_Gana_Local(1)]
        probabilidades = modelo.predict_proba(df_partido)[0]
        prob_Visita = probabilidades[0] * 100 
        prob_Local = probabilidades[1] * 100 
        
        print(f"⚾ {equipo_visita} @ {equipo_local}")
        print(f"🏦 {casa_apuestas} | Cuotas -> Visita: {cuota_V} | Local: {cuota_L}")
        print(f"📊 IA Predictiva -> Visita: {prob_Visita:.1f}% | Local: {prob_Local:.1f}%")
        
        valor_encontrado = False
        
        if cuota_V > 0 and (prob_Visita/100) > (1/cuota_V):
            apuesta = calcular_kelly(prob_Visita, cuota_V, CAPITAL_TOTAL)
            if apuesta > 0:
                print(f"✅ ¡VALOR EN VISITANTE! Invertir: ${apuesta} USD en {equipo_visita}")
                valor_encontrado = True
                
        if cuota_L > 0 and (prob_Local/100) > (1/cuota_L):
            apuesta = calcular_kelly(prob_Local, cuota_L, CAPITAL_TOTAL)
            if apuesta > 0:
                print(f"✅ ¡VALOR EN LOCAL! Invertir: ${apuesta} USD en {equipo_local}")
                valor_encontrado = True
            
        if not valor_encontrado:
            print("⛔ Sin ventaja. Mantener efectivo.")
            
        print("-" * 60)

if __name__ == "__main__":
    escanear_mercado_mlb()