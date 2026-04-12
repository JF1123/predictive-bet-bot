import pandas as pd
import xgboost as xgb
import joblib

def escaner_tiempo_real():
    print("🌐 Iniciando Escáner de Partidos en Vivo...")
    
    # 1. Cargar el cerebro entrenado
    try:
        modelo = joblib.load('oraculo_xgboost.pkl')
        print("🧠 Cerebro XGBoost cargado exitosamente.")
    except:
        print("❌ Error: No se encontró el cerebro. ¿Ejecutaste el backtest para guardarlo?")
        return

    # 2. Simulamos leer la API de BetPlay para el partido de este fin de semana:
    # Ejemplo: Millonarios (Local) vs Atlético Nacional (Visitante)
    print("\n📡 Recibiendo datos de cuotas desde BetPlay / Rushbet...")
    
    # Supongamos que calculamos sus Elos y formas actuales
    partido_hoy = {
        'HomeElo': 1520.5,      # Millonarios
        'AwayElo': 1580.2,      # Nacional (Supongamos que viene mejor)
        'EloDifference': -59.7, # Nacional es superior históricamente
        'Form5Home': 7,         # Millos hizo 7 puntos de 15 recientes
        'Form5Away': 12,        # Nacional hizo 12 puntos de 15
        'FormDifference': -5    # Inercia a favor de Nacional
    }
    
    # Cuotas que está pagando BetPlay en este momento
    cuotas_betplay = {'1': 2.80, 'X': 3.10, '2': 2.45}
    
    # Convertimos a formato que entiende la IA
    df_partido = pd.DataFrame([partido_hoy])
    
    # 3. El Oráculo hace su predicción
    print("\n🔮 Analizando la matemática del partido...")
    probabilidades = modelo.predict_proba(df_partido)[0]
    
    # Asumiendo el orden interno de las clases: 0=A(Visitante), 1=D(Empate), 2=H(Local)
    # *Nota: Esto depende de cómo lo guardó LabelEncoder, pero asumiremos este orden general
    prob_A = probabilidades[0] * 100
    prob_D = probabilidades[1] * 100
    prob_H = probabilidades[2] * 100
    
    print("-" * 40)
    print("⚽ MILLONARIOS vs ATL. NACIONAL")
    print(f"📊 Probabilidad IA -> Local (1): {prob_H:.1f}% | Empate (X): {prob_D:.1f}% | Visitante (2): {prob_A:.1f}%")
    print("💰 Cuotas BetPlay -> Local (1): 2.80 | Empate (X): 3.10 | Visitante (2): 2.45")
    print("-" * 40)
    
    # 4. Buscando el "Valor" (Criterio de Kelly simple)
    print("\n🤖 Decisión del Bot de Trading:")
    if (prob_H/100) > (1/cuotas_betplay['1']):
        print(f"✅ ¡ALERTA DE VALOR! Apostar al LOCAL (1). La cuota 2.80 subestima a Millonarios.")
    elif (prob_A/100) > (1/cuotas_betplay['2']):
        print(f"✅ ¡ALERTA DE VALOR! Apostar al VISITANTE (2). Nacional tiene más probabilidad de la que paga BetPlay.")
    else:
        print("⛔ NO APOSTAR. Las cuotas de BetPlay están bien ajustadas. No hay ventaja matemática.")

if __name__ == "__main__":
    escaner_tiempo_real()