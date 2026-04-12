import pandas as pd
import os
import xgboost as xgb
import joblib # Librería para guardar modelos
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import warnings

warnings.filterwarnings('ignore')

def calcular_kelly_conservador(prob_modelo, cuota, margen_seguridad=0.05):
    """Kelly fraccional hiper-protegido"""
    if cuota <= 1.0:
        return 0.0
        
    prob_implicita_bookie = 1.0 / cuota
    
    ventaja_neta = prob_modelo - prob_implicita_bookie
    if ventaja_neta < margen_seguridad:
        return 0.0
        
    b = cuota - 1.0
    p = prob_modelo
    q = 1.0 - p
    f_star = (b * p - q) / b
    
    inversion_sugerida = max(0.0, f_star / 10.0)
    return min(inversion_sugerida, 0.03)

def ejecutar_backtest_xgboost():
    carpeta_datos = "Club-Football-Match-Data-2000-2025/data"
    archivos_reales = os.listdir(carpeta_datos)
    
    ruta_archivo = None
    for archivo in archivos_reales:
        if "match" in archivo.lower() and archivo.endswith(".csv"):
            ruta_archivo = os.path.join(carpeta_datos, archivo)
            break
            
    print("🚀 Iniciando Simulador Quant con Motor XGBoost...")
    df = pd.read_csv(ruta_archivo, low_memory=False)
    
    columnas_necesarias = ['MatchDate', 'HomeElo', 'AwayElo', 'Form5Home', 'Form5Away', 'FTResult', 'OddHome', 'OddDraw', 'OddAway']
    df_limpio = df[columnas_necesarias].dropna().copy()
    df_limpio = df_limpio.sort_values(by='MatchDate')
    
    df_limpio['EloDifference'] = df_limpio['HomeElo'] - df_limpio['AwayElo']
    df_limpio['FormDifference'] = df_limpio['Form5Home'] - df_limpio['Form5Away']
    
    X = df_limpio[['HomeElo', 'AwayElo', 'EloDifference', 'Form5Home', 'Form5Away', 'FormDifference']]
    
    # XGBoost no entiende letras, necesita números. Traducimos H, D, A a 0, 1, 2
    traductor = LabelEncoder()
    y_numerico = traductor.fit_transform(df_limpio['FTResult'])
    
    X_train, X_test, y_train, y_test = train_test_split(X, y_numerico, test_size=0.2, shuffle=False)
    df_test = df_limpio.loc[X_test.index]
    
    print(f"📚 XGBoost está devorando {len(X_train):,} partidos históricos...")
    # Configuración base de XGBoost
    modelo = xgb.XGBClassifier(
        n_estimators=150, 
        learning_rate=0.05, 
        max_depth=5, 
        eval_metric='mlogloss',
        random_state=42
    )
    modelo.fit(X_train, y_train)
    joblib.dump(modelo, 'oraculo_xgboost.pkl')
    print("💾 Cerebro de XGBoost guardado en el disco duro!")
    
    print("🔮 Simulando predicciones futuras...")
    probabilidades = modelo.predict_proba(X_test)
    
    # Identificamos qué número le asignó a cada resultado
    clases_originales = traductor.classes_
    idx_H = list(clases_originales).index('H')
    idx_D = list(clases_originales).index('D')
    idx_A = list(clases_originales).index('A')
    
    capital_inicial = 1000.0
    capital_actual = capital_inicial
    apuestas_realizadas = 0
    apuestas_ganadas = 0
    dinero_maximo = capital_inicial
    
    print("⏳ Ejecutando inversiones... por favor espera.")
    
    for i in range(len(X_test)):
        if capital_actual <= 0:
            print("💥 BANCARROTA.")
            break
            
        prob_H, prob_D, prob_A = probabilidades[i][idx_H], probabilidades[i][idx_D], probabilidades[i][idx_A]
        cuota_H, cuota_D, cuota_A = df_test.iloc[i]['OddHome'], df_test.iloc[i]['OddDraw'], df_test.iloc[i]['OddAway']
        
        kelly_H = calcular_kelly_conservador(prob_H, cuota_H, margen_seguridad=0.05)
        kelly_D = calcular_kelly_conservador(prob_D, cuota_D, margen_seguridad=0.05)
        kelly_A = calcular_kelly_conservador(prob_A, cuota_A, margen_seguridad=0.05)
        
        mejor_opcion, mejor_kelly, cuota_apostada = None, 0, 0
        
        if kelly_H > mejor_kelly: mejor_opcion, mejor_kelly, cuota_apostada = 'H', kelly_H, cuota_H
        if kelly_D > mejor_kelly: mejor_opcion, mejor_kelly, cuota_apostada = 'D', kelly_D, cuota_D
        if kelly_A > mejor_kelly: mejor_opcion, mejor_kelly, cuota_apostada = 'A', kelly_A, cuota_A
            
        if mejor_opcion is not None:
            apuestas_realizadas += 1
            riesgo = capital_actual * mejor_kelly 
            capital_actual -= riesgo 
            
            if df_test.iloc[i]['FTResult'] == mejor_opcion:
                capital_actual += (riesgo * cuota_apostada)
                apuestas_ganadas += 1
                
            if capital_actual > dinero_maximo:
                dinero_maximo = capital_actual
                
    print("\n📊 --- RESULTADOS FINANCIEROS CON XGBOOST ---")
    print(f"💰 Capital Inicial:   ${capital_inicial:,.2f}")
    print(f"💰 Capital Final:     ${capital_actual:,.2f}")
    print(f"🚀 Capital Máximo Alcanzado: ${dinero_maximo:,.2f}")
    roi = ((capital_actual - capital_inicial) / capital_inicial) * 100
    print(f"📈 Retorno de Inversión (ROI): {roi:,.2f}%")
    print(f"🎯 Total de apuestas realizadas: {apuestas_realizadas:,}")
    if apuestas_realizadas > 0:
        win_rate = (apuestas_ganadas / apuestas_realizadas) * 100
        print(f"✅ Win Rate: {win_rate:.2f}%")

if __name__ == "__main__":
    ejecutar_backtest_xgboost()