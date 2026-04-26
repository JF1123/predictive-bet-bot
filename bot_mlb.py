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
REGION = 'us,eu'
ARCHIVO_CACHE = 'cache_mlb.json'
ARCHIVO_LEDGER = 'ledger_simulacion.csv'
HORAS_VIGENCIA = 6
CAPITAL_TOTAL = 20000.00 
# TU URL DE DISCORD
DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1493025221370843317/1AujEKaPM8t_17ZbrRDLf3iAftZ1D1H3T72eDWvIo91Ub27Bx4_iCW2lavHOd0JBp1Q_'

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
import pandas as pd

def generar_resumen_financiero(ruta_csv='ledger_simulacion.csv', capital_inicial=20000.0):
    try:
        df = pd.read_csv(ruta_csv)
    except FileNotFoundError:
        return "🐝 **REPORTE DEL ENJAMBRE** 🐝\n\nArchivo de datos no encontrado.\n\n🎯 **APUESTAS PARA HOY:**\n"
    
    # Filtrar solo las apuestas que ya tienen resultado
    df_completadas = df[df['Estado'].isin(['Ganada', 'Perdida', 'Empate'])]
    
    # Calcular Finanzas
    beneficio_total = df_completadas['Beneficio_Neto'].sum()
    capital_actual = capital_inicial + beneficio_total
    roi = (beneficio_total / capital_inicial) * 100 if capital_inicial > 0 else 0
    
    # Historial de victorias
    ganadas = len(df[df['Estado'] == 'Ganada'])
    perdidas = len(df[df['Estado'] == 'Perdida'])
    
    # Extraer los resultados del último día completado ("ayer")
    if not df_completadas.empty:
        ultima_fecha = df_completadas['Fecha'].max()
        resultados_ayer = df_completadas[df_completadas['Fecha'] == ultima_fecha]
        
        texto_resultados = f"🏟️ **RESULTADOS DEL {ultima_fecha}:**\n"
        for _, row in resultados_ayer.iterrows():
            if row['Estado'] == 'Ganada':
                icono = "✅ GANADA"
            elif row['Estado'] == 'Perdida':
                icono = "❌ PERDIDA"
            else:
                icono = "➖ EMPATE"
                
            signo = "+" if row['Beneficio_Neto'] > 0 else ""
            texto_resultados += f"• {row['Visita']} vs {row['Local']}: {icono} ({signo}${row['Beneficio_Neto']:.0f})\n"
    else:
        texto_resultados = "🏟️ **RESULTADOS DE AYER:**\n• Aún no hay partidos liquidados en el registro.\n"
        
    # Ensamblar el mensaje final
    mensaje = (
        f"🐝 **REPORTE DEL ENJAMBRE** 🐝\n\n"
        f"📈 **BALANCE GENERAL:**\n"
        f"• Capital Inicial: ${capital_inicial:,.0f} COP\n"
        f"• Capital Actual: ${capital_actual:,.0f} COP (**{roi:+.1f}%**)\n"
        f"• Historial: {ganadas} Ganadas / {perdidas} Perdidas\n\n"
        f"{texto_resultados}\n"
        f"🎯 **APUESTAS PARA HOY:**\n"
    )
    return mensaje
def enviar_alerta_discord(mensaje):
    datos = {
        "content": mensaje,
        "username": "Enjambre Quant MLB",
        "avatar_url": "https://cdn-icons-png.flaticon.com/512/2043/2043869.png"
    }
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=datos)
    except Exception as e:
        print(f"⚠️ Error enviando a Discord: {e}")

def calcular_kelly(probabilidad_ia, cuota, bankroll):
    p = probabilidad_ia / 100.0 
    fraccion_kelly = ((p * cuota) - 1) / (cuota - 1)
    fraccion_segura = fraccion_kelly * 0.25 
    if fraccion_segura > 0.05: fraccion_segura = 0.05
    if fraccion_segura <= 0: return 0.0
    
    apuesta = round(bankroll * fraccion_segura, 2)
    if apuesta < 500: return 0.0 
    return apuesta

def guardar_apuesta_simulada(fecha, visita, local, equipo_apuesta, cuota, casa, inversion, prob_ia):
    ganancia_potencial = round((inversion * cuota) - inversion, 2)
    nueva_apuesta = pd.DataFrame([{
        'Fecha': fecha, 'Visita': visita, 'Local': local,
        'Apuesta_A': equipo_apuesta, 'Cuota': cuota,
        'Casa_Apuestas': casa, 'Inversion_COP': inversion,
        'Ganancia_Potencial_COP': ganancia_potencial,
        'Prob_IA_%': prob_ia, 'Estado': 'Pendiente', 'Beneficio_Neto': 0.0
    }])
    if os.path.exists(ARCHIVO_LEDGER):
        df_ledger = pd.read_csv(ARCHIVO_LEDGER)
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
            with open(ARCHIVO_CACHE, 'r') as f: return json.load(f)
    url = f'https://api.the-odds-api.com/v4/sports/{DEPORTE}/odds/?apiKey={API_KEY}&regions={REGION}&markets={MERCADO}'
    respuesta = requests.get(url)
    if respuesta.status_code == 200:
        datos = respuesta.json()
        with open(ARCHIVO_CACHE, 'w') as f: json.dump(datos, f)
        return datos
    return None

def buscar_cuota_preferida(bookmakers, equipo_visita, equipo_local):
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
        print("❌ Error de archivos.")
        return

    partidos = obtener_datos_api()
    if not partidos: return
    stats = df_historico.mean(numeric_only=True)
    hoy = datetime.now().strftime('%Y-%m-%d')

    print(f"\n💵 CAPITAL VIRTUAL: ${CAPITAL_TOTAL} COP")
    print("🤖 Generando simulaciones y buscando valor...")

    # 1. CREAMOS EL ENCABEZADO FINANCIERO DEL MENSAJE
    mensaje_discord = generar_resumen_financiero(ARCHIVO_LEDGER, CAPITAL_TOTAL)
    apuestas_encontradas = 0

    for partido in partidos:
        if not partido['bookmakers']: continue
        eq_v, eq_l = partido['away_team'], partido['home_team']
        casa, c_v, c_l = buscar_cuota_preferida(partido['bookmakers'], eq_v, eq_l)
        
        datos_pred = pd.DataFrame([{'Ofensiva_L': stats['Carreras_Local'], 'Ofensiva_V': stats['Carreras_Visita'], 'Defensa_L': stats['Carreras_Visita'], 'Defensa_V': stats['Carreras_Local'], 'Racha_Ofensiva_L': stats['Carreras_Local'], 'Racha_Ofensiva_V': stats['Carreras_Visita'], 'Pitcher_L_ERA_Proxy': stats['Carreras_Visita'], 'Pitcher_V_ERA_Proxy': stats['Carreras_Local']}])
        probs = modelo.predict_proba(datos_pred)[0]
        p_v, p_l = round(probs[0] * 100, 1), round(probs[1] * 100, 1)
        
        print(f"⚾ {eq_v} @ {eq_l}")
        val_f = False

        # Lógica de apuesta
        for eq, cuota, prob in [(eq_v, c_v, p_v), (eq_l, c_l, p_l)]:
            if cuota > 0 and (prob/100) > (1/cuota):
                apuesta = calcular_kelly(prob, cuota, CAPITAL_TOTAL)
                if apuesta > 0:
                    # 2. AGREGAMOS CADA APUESTA AL MENSAJE CONSOLIDADO
                    texto_apuesta = f"⚾ **{eq_v} vs {eq_l}**\n👉 Invertir: **${apuesta:,.0f} COP** en **{eq}**\n🏦 Casa: {casa} (Cuota: {cuota})\n"
                    print(f"✅ VALOR ENCONTRADO: {eq} a cuota {cuota}")
                    
                    guardar_apuesta_simulada(hoy, eq_v, eq_l, eq, cuota, casa, apuesta, prob)
                    mensaje_discord += texto_apuesta + "\n"
                    apuestas_encontradas += 1
                    val_f = True
        
        if not val_f: print("⛔ Sin ventaja.")

    # 3. SI NO HAY APUESTAS, LO AVISAMOS. LUEGO ENVIAMOS EL MENSAJE ÚNICO.
    if apuestas_encontradas == 0:
        mensaje_discord += "😴 El modelo no encontró ventajas matemáticas hoy. Capital protegido."
        
    enviar_alerta_discord(mensaje_discord)

if __name__ == "__main__":
    escanear_mercado_mlb()