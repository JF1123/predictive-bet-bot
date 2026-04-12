import requests
import pandas as pd
import joblib
import warnings
import json
import os
from datetime import datetime, timedelta

warnings.filterwarnings('ignore')

# --- CONFIGURACIÓN QUANT ---
API_KEY = '059df6f2341b819b810c4fcab8de323e' # ¡No olvides poner tu llave real!
DEPORTE = 'baseball_mlb' 
MERCADO = 'h2h' 
REGION = 'us,eu' # Añadimos 'eu' para acceder a Unibet (Proxy de Rushbet) y Pinnacle
ARCHIVO_CACHE = 'cache_mlb.json'
ARCHIVO_LEDGER = 'ledger_simulacion.csv'
HORAS_VIGENCIA = 6
CAPITAL_TOTAL = 20000.00 

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
    fraccion_segura = fraccion_kelly * 0.25 
    if fraccion_segura > 0.05: fraccion_segura = 0.05
    if fraccion_segura <= 0: return 0.0
    return round(bankroll * fraccion_segura, 2)

def guardar_apuesta_simulada(fecha, visita, local, equipo_apuesta, cuota, casa, inversion, prob_ia):
    # Calcular la ganancia potencial
    ganancia_potencial = round((inversion * cuota) - inversion, 2)
    
    nueva_apuesta = pd.DataFrame([{
        'Fecha': fecha,
        'Visita': visita,
        'Local': local,
        'Apuesta_A': equipo_apuesta,
        'Cuota': cuota,
        'Casa_Apuestas': casa,
        'Inversion_USD': inversion,
        'Ganancia_Potencial_USD': ganancia_potencial,
        'Prob_IA_%': prob_ia,
        'Estado': 'Pendiente', # Cambiará a Ganada/Perdida con el Updater
        'Beneficio_Neto': 0.0
    }])
    
    if os.path.exists(ARCHIVO_LEDGER):
        df_ledger = pd.read_csv(ARCHIVO_LEDGER)
        # Evitar duplicados si corremos el bot varias veces el mismo día
        duplicado = df_ledger[(df_ledger['Fecha'] == fecha) & (df_ledger['Apuesta_A'] == equipo_apuesta)]
        if duplicado.empty:
            df_ledger = pd.concat([df_ledger, nueva_apuesta], ignore_index=True)
            df_ledger.to_csv(ARCHIVO_LEDGER, index=False)
    else:
        nueva_apuesta.to_csv(ARCHIVO_LEDGER, index=False)

def obtener_datos_api():
    if os.path.exists(ARCHIVO_CACHE):
        tiempo_modificacion = datetime.fromtimestamp(os.path.getmtime(ARCHIVO_CACHE))
        if datetime.now() - tiempo_modificacion < timedelta(hours=HORAS_VIGENCIA):
            with open(ARCHIVO_CACHE, 'r') as f:
                return json.load(f)

    url = f'https://api.the-odds-api.com/v4/sports/{DEPORTE}/odds/?apiKey={API_KEY}&regions={REGION}&markets={MERCADO}'
    respuesta = requests.get(url)
    
    if respuesta.status_code == 200:
        datos = respuesta.json()
        with open(ARCHIVO_CACHE, 'w') as f:
            json.dump(datos, f)
        return datos
    return None

def buscar_cuota_preferida(bookmakers, equipo_visita, equipo_local):
    # Buscamos primero Unibet (proxy de Rushbet/Kambi), BetRivers, Pinnacle o nos quedamos con la primera que haya
    casas_preferidas = ['unibet', 'betrivers', 'pinnacle', 'bet365', 'fanduel']
    
    for preferida in casas_preferidas:
        for bookie in bookmakers:
            if preferida.lower() in bookie['key'].lower():
                cuotas = bookie['markets'][0]['outcomes']
                v, l = 0.0, 0.0
                for op in cuotas:
                    if op['name'] == equipo_visita: v = op['price']
                    elif op['name'] == equipo_local: l = op['price']
                return bookie['title'], v, l
                
    # Si no hay ninguna preferida, tomamos la primera disponible
    bookie = bookmakers[0]
    cuotas = bookie['markets'][0]['outcomes']
    v, l = 0.0, 0.0
    for op in cuotas:
        if op['name'] == equipo_visita: v = op['price']
        elif op['name'] == equipo_local: l = op['price']
    return bookie['title'], v, l

def escanear_mercado_mlb():
    try:
        modelo = joblib.load('oraculo_mlb_xgboost.pkl')
        df_historico = pd.read_csv('mlb_historico.csv')
    except:
        print("❌ Faltan archivos maestros. Ejecuta el minero y el train primero.")
        return

    partidos = obtener_datos_api()
    if not partidos: return
    
    # Calcular promedios globales rápidos para inyectar al modelo
    stats = df_historico.mean(numeric_only=True)
    hoy = datetime.now().strftime('%Y-%m-%d')

    print(f"\n💵 CAPITAL VIRTUAL: ${CAPITAL_TOTAL} USD")
    print("🤖 Generando simulaciones de Paper Trading...\n")
    print("=" * 60)
    
    for partido in partidos:
        if not partido['bookmakers']: continue
            
        equipo_visita = partido['away_team']
        equipo_local = partido['home_team']
        
        casa_nombre, cuota_V, cuota_L = buscar_cuota_preferida(partido['bookmakers'], equipo_visita, equipo_local)
        
        # Inyectar datos promedio para la simulación rápida (El V2 necesita 8 features)
        datos_pred = pd.DataFrame([{
            'Ofensiva_L': stats['Carreras_Local'], 'Ofensiva_V': stats['Carreras_Visita'],
            'Defensa_L': stats['Carreras_Visita'], 'Defensa_V': stats['Carreras_Local'],
            'Racha_Ofensiva_L': stats['Carreras_Local'], 'Racha_Ofensiva_V': stats['Carreras_Visita'],
            'Pitcher_L_ERA_Proxy': stats['Carreras_Visita'], 'Pitcher_V_ERA_Proxy': stats['Carreras_Local']
        }])
        
        probabilidades = modelo.predict_proba(datos_pred)[0]
        prob_Visita = round(probabilidades[0] * 100, 1)
        prob_Local = round(probabilidades[1] * 100, 1)
        
        print(f"⚾ {equipo_visita} @ {equipo_local}")
        print(f"🏦 Casa: {casa_nombre} | Cuotas -> V: {cuota_V} | L: {cuota_L}")
        
        valor_encontrado = False
        
        if cuota_V > 0 and (prob_Visita/100) > (1/cuota_V):
            apuesta = calcular_kelly(prob_Visita, cuota_V, CAPITAL_TOTAL)
            if apuesta > 0:
                print(f"✅ VALOR VIRTUAL: Invertir ${apuesta} en {equipo_visita}")
                guardar_apuesta_simulada(hoy, equipo_visita, equipo_local, equipo_visita, cuota_V, casa_nombre, apuesta, prob_Visita)
                valor_encontrado = True
                
        if cuota_L > 0 and (prob_Local/100) > (1/cuota_L):
            apuesta = calcular_kelly(prob_Local, cuota_L, CAPITAL_TOTAL)
            if apuesta > 0:
                print(f"✅ VALOR VIRTUAL: Invertir ${apuesta} en {equipo_local}")
                guardar_apuesta_simulada(hoy, equipo_visita, equipo_local, equipo_local, cuota_L, casa_nombre, apuesta, prob_Local)
                valor_encontrado = True
            
        if not valor_encontrado: print("⛔ Sin ventaja matemática.")
        print("-" * 60)

if __name__ == "__main__":
    escanear_mercado_mlb()