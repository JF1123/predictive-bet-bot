import requests
import pandas as pd
import joblib
import warnings
import json
import os
from datetime import datetime, timedelta

warnings.filterwarnings('ignore')

# --- CONFIGURACIÓN ---
API_KEY = '059df6f2341b819b810c4fcab8de323e' 
DEPORTE = 'soccer_epl' 
MERCADO = 'h2h' 
REGION = 'us,eu,uk' 
ARCHIVO_CACHE = 'cache_partidos.json'
HORAS_VIGENCIA = 12

def cargar_base_historica():
    """Carga el CSV gigante a la memoria RAM una sola vez"""
    print("📚 Cargando base de datos histórica de Elos...")
    carpeta_datos = "Club-Football-Match-Data-2000-2025/data"
    
    if not os.path.exists(carpeta_datos):
        print("❌ Error: No encuentro la carpeta de datos.")
        return None
        
    archivos_reales = os.listdir(carpeta_datos)
    ruta_archivo = None
    for archivo in archivos_reales:
        if "match" in archivo.lower() and archivo.endswith(".csv"):
            ruta_archivo = os.path.join(carpeta_datos, archivo)
            break
            
    if ruta_archivo:
        # Cargamos asumiendo que las columnas de nombre de equipo son Home y Away
        df = pd.read_csv(ruta_archivo, low_memory=False)
        df = df.sort_values(by='MatchDate', ascending=False) # Ordenamos del más reciente al más viejo
        return df
    return None

def obtener_stats_reales(equipo, df_historico):
    """Busca el Elo y Form REAL del equipo en su último partido jugado"""
    if df_historico is None:
        return {'Elo': 1500.0, 'Form': 7} # Respaldo de emergencia
        
    # Usamos las primeras 5 letras para evitar problemas entre "Wolves" y "Wolverhampton"
    nombre_busqueda = equipo[:5].lower()
    
    # Asumimos que las columnas en tu CSV original se llaman 'Home' y 'Away' o 'HomeTeam' y 'AwayTeam'
    # Intentaremos con 'Home' y 'Away' que es el estándar habitual
    col_home = 'Home' if 'Home' in df_historico.columns else 'HomeTeam'
    col_away = 'Away' if 'Away' in df_historico.columns else 'AwayTeam'
    
    # Filtramos los partidos donde el equipo haya jugado
    mask_local = df_historico[col_home].astype(str).str.lower().str.contains(nombre_busqueda, na=False)
    mask_visita = df_historico[col_away].astype(str).str.lower().str.contains(nombre_busqueda, na=False)
    
    df_equipo = df_historico[mask_local | mask_visita]
    
    if df_equipo.empty:
        # Si de verdad no existe (ej. equipo recién ascendido), le damos un Elo bajo
        print(f"⚠️ No se encontró historial para {equipo}. Asignando Elo de novato.")
        return {'Elo': 1300.0, 'Form': 5}
        
    ultimo_partido = df_equipo.iloc[0] # El más reciente (la fila 0)
    
    # Revisamos si en ese último partido jugó de Local o de Visita para sacar su Elo correcto
    if str(ultimo_partido[col_home]).lower().startswith(nombre_busqueda):
        return {'Elo': ultimo_partido['HomeElo'], 'Form': ultimo_partido['Form5Home']}
    else:
        return {'Elo': ultimo_partido['AwayElo'], 'Form': ultimo_partido['Form5Away']}

def obtener_datos_api():
    if os.path.exists(ARCHIVO_CACHE):
        tiempo_modificacion = datetime.fromtimestamp(os.path.getmtime(ARCHIVO_CACHE))
        if datetime.now() - tiempo_modificacion < timedelta(hours=HORAS_VIGENCIA):
            print("📦 Leyendo datos desde el Caché local (0 Créditos gastados).")
            with open(ARCHIVO_CACHE, 'r') as f:
                return json.load(f)

    print("🌐 Caché vacío o caducado. Consumiendo 1 crédito de The Odds API...")
    url = f'https://api.the-odds-api.com/v4/sports/{DEPORTE}/odds/?apiKey={API_KEY}&regions={REGION}&markets={MERCADO}'
    respuesta = requests.get(url)
    
    if respuesta.status_code == 200:
        datos = respuesta.json()
        if len(datos) == 0:
            print(f"⚠️ La API se conectó bien, pero dice que hay 0 partidos de '{DEPORTE}' disponibles en la región '{REGION}'.")
        with open(ARCHIVO_CACHE, 'w') as f:
            json.dump(datos, f)
        return datos
    else:
        print(f"❌ Error de la API ({respuesta.status_code}): {respuesta.text}")
        return None
def escanear_mercado():
    try:
        modelo = joblib.load('oraculo_xgboost.pkl')
    except Exception as e:
        print("❌ Error: No se encontró el cerebro.")
        return

    df_historico = cargar_base_historica()
    partidos = obtener_datos_api()
    
    if not partidos:
        return

    print("\n🔍 Analizando oportunidades con Datos Reales...\n")
    print("-" * 50)
    
    for partido in partidos[:3]:
        equipo_local = partido['home_team']
        equipo_visita = partido['away_team']
        
        if not partido['bookmakers']:
            continue
            
        casa_apuestas = partido['bookmakers'][0]['title']
        cuotas = partido['bookmakers'][0]['markets'][0]['outcomes']
        
        cuota_1 = cuota_X = cuota_2 = 0.0
        for opcion in cuotas:
            if opcion['name'] == equipo_local: cuota_1 = opcion['price']
            elif opcion['name'] == equipo_visita: cuota_2 = opcion['price']
            elif opcion['name'] == 'Draw': cuota_X = opcion['price']
            
        # AQUÍ OCURRE LA MAGIA: Buscamos en el CSV
        stats_local = obtener_stats_reales(equipo_local, df_historico)
        stats_visita = obtener_stats_reales(equipo_visita, df_historico)
        
        datos_partido = {
            'HomeElo': stats_local['Elo'],
            'AwayElo': stats_visita['Elo'],
            'EloDifference': stats_local['Elo'] - stats_visita['Elo'],
            'Form5Home': stats_local['Form'],
            'Form5Away': stats_visita['Form'],
            'FormDifference': stats_local['Form'] - stats_visita['Form']
        }
        
        df_partido = pd.DataFrame([datos_partido])
        probabilidades = modelo.predict_proba(df_partido)[0]
        prob_A = probabilidades[0] * 100 
        prob_D = probabilidades[1] * 100 
        prob_H = probabilidades[2] * 100 
        
        print(f"⚽ {equipo_local} (Elo: {stats_local['Elo']:.0f}) vs {equipo_visita} (Elo: {stats_visita['Elo']:.0f})")
        print(f"🏦 Casa: {casa_apuestas}")
        print(f"💰 Cuotas  -> Local: {cuota_1} | Empate: {cuota_X} | Visita: {cuota_2}")
        print(f"📊 XGBoost -> Local: {prob_H:.1f}% | Empate: {prob_D:.1f}% | Visita: {prob_A:.1f}%")
        
        valor_encontrado = False
        if cuota_1 > 0 and (prob_H/100) > (1/cuota_1):
            print(f"✅ ¡VALOR! Apostar al Local ({equipo_local}) a cuota {cuota_1}")
            valor_encontrado = True
        if cuota_2 > 0 and (prob_A/100) > (1/cuota_2):
            print(f"✅ ¡VALOR! Apostar al Visitante ({equipo_visita}) a cuota {cuota_2}")
            valor_encontrado = True
            
        if not valor_encontrado:
            print("⛔ Sin ventaja matemática.")
            
        print("-" * 50)

if __name__ == "__main__":
    escanear_mercado()