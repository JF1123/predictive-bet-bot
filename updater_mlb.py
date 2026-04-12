import statsapi
import pandas as pd
from datetime import datetime, timedelta
import os
import subprocess

# --- Mapeo de equipos ---
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
def calcular_kelly(probabilidad_ia, cuota, bankroll):
    p = probabilidad_ia / 100.0 
    fraccion_kelly = ((p * cuota) - 1) / (cuota - 1)
    fraccion_segura = fraccion_kelly * 0.25 
    if fraccion_segura > 0.05: fraccion_segura = 0.05
    if fraccion_segura <= 0: return 0.0
    
    apuesta = round(bankroll * fraccion_segura, 2)
    
    # 🛑 NUEVA REGLA QUANT: Filtro de Apuesta Mínima Rushbet
    if apuesta < 500:
        return 0.0 
        
    return apuesta
def auditar_apuestas():
    archivo_ledger = 'ledger_simulacion.csv'
    archivo_hist = 'mlb_historico.csv'
    
    if not os.path.exists(archivo_ledger) or not os.path.exists(archivo_hist):
        return

    print("⚖️ Auditando resultados y liquidando apuestas...")
    df_ledger = pd.read_csv(archivo_ledger)
    df_hist = pd.read_csv(archivo_hist)
    
    # Solo procesamos las que están 'Pendiente'
    for i, fila in df_ledger.iterrows():
        if fila['Estado'] == 'Pendiente':
            # Buscamos el partido en el histórico
            partido = df_hist[
                (df_hist['Fecha'] == fila['Fecha']) & 
                ((df_hist['Visita'] == fila['Visita']) | (df_hist['Local'] == fila['Local']))
            ]
            
            if not partido.empty:
                ganador_real = partido.iloc[0]['Local'] if partido.iloc[0]['Gana_Local'] == 1 else partido.iloc[0]['Visita']
                equipo_apostado = fila['Apuesta_A']
                
                # Mapear nombre completo a código si es necesario
                cod_apostado = MAPEO_INVERSO.get(equipo_apostado, equipo_apostado)
                
                if cod_apostado == ganador_real:
                    df_ledger.at[i, 'Estado'] = 'Ganada'
                    df_ledger.at[i, 'Beneficio_Neto'] = fila['Ganancia_Potencial_USD']
                else:
                    df_ledger.at[i, 'Estado'] = 'Perdida'
                    df_ledger.at[i, 'Beneficio_Neto'] = -fila['Inversion_USD']

    df_ledger.to_csv(archivo_ledger, index=False)
    
    # --- GENERAR PLANILLA SEMANAL ---
    print("\n" + "="*40)
    print("📊 PLANILLA DE RENDIMIENTO (Paper Trading)")
    total_invertido = df_ledger['Inversion_USD'].sum()
    balance_neto = df_ledger['Beneficio_Neto'].sum()
    roi = (balance_neto / total_invertido) * 100 if total_invertido > 0 else 0
    
    print(f"💰 Balance Total: {balance_neto:+.2f} COP")
    print(f"📈 ROI: {roi:.2f}%")
    print(f"✅ Aciertos: {len(df_ledger[df_ledger['Estado'] == 'Ganada'])}")
    print(f"❌ Fallos: {len(df_ledger[df_ledger['Estado'] == 'Perdida'])}")
    print("="*40 + "\n")

# ... (Mantén el resto de tu función actualizar_cerebro_diario igual) ...

if __name__ == "__main__":
    # 1. Actualizar datos de la MLB
    # actualizar_cerebro_diario() # (Ya lo tienes configurado)
    
    # 2. Auditar apuestas de ayer
    auditar_apuestas()