import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score
import joblib

def enriquecer_datos_mlb(df):
    print("🧪 Procesando Sabermetría Avanzada...")
    
    # Asegurar orden cronológico estricto (vital para no espiar el futuro)
    df = df.sort_values(by='Fecha').reset_index(drop=True)
    
    # 1. Promedios Históricos Acumulados
    df['Ofensiva_L'] = df.groupby('Local')['Carreras_Local'].transform(lambda x: x.shift().expanding().mean())
    df['Ofensiva_V'] = df.groupby('Visita')['Carreras_Visita'].transform(lambda x: x.shift().expanding().mean())
    df['Defensa_L'] = df.groupby('Local')['Carreras_Visita'].transform(lambda x: x.shift().expanding().mean())
    df['Defensa_V'] = df.groupby('Visita')['Carreras_Local'].transform(lambda x: x.shift().expanding().mean())
    
    # 2. Momentum (Racha de los últimos 10 partidos)
    df['Racha_Ofensiva_L'] = df.groupby('Local')['Carreras_Local'].transform(lambda x: x.shift().rolling(10).mean())
    df['Racha_Ofensiva_V'] = df.groupby('Visita')['Carreras_Visita'].transform(lambda x: x.shift().rolling(10).mean())
    
    # 3. Factor Pitcher (Carreras permitidas por el pitcher abridor histórico)
    df['Pitcher_L_ERA_Proxy'] = df.groupby('Pitcher_Local')['Carreras_Visita'].transform(lambda x: x.shift().expanding().mean())
    df['Pitcher_V_ERA_Proxy'] = df.groupby('Pitcher_Visita')['Carreras_Local'].transform(lambda x: x.shift().expanding().mean())
    
    # Los novatos o datos sin historia se rellenan con el promedio global de la liga
    promedios = df.mean(numeric_only=True)
    df = df.fillna(promedios)
    
    return df

def entrenar_cerebro_v2():
    print("🧠 Iniciando el Laboratorio Quant (Cerebro V2) para MLB...")
    
    try:
        df = pd.read_csv('mlb_historico.csv')
        df['Fecha'] = pd.to_datetime(df['Fecha'])
    except:
        print("❌ Error: No se encontró 'mlb_historico.csv'. Ejecuta el minero primero.")
        return

    df = enriquecer_datos_mlb(df)
    
    # Variables predictoras (Ahora son 8 dimensiones en lugar de 4)
    features = [
        'Ofensiva_L', 'Ofensiva_V', 'Defensa_L', 'Defensa_V',
        'Racha_Ofensiva_L', 'Racha_Ofensiva_V', 
        'Pitcher_L_ERA_Proxy', 'Pitcher_V_ERA_Proxy'
    ]
    
    X = df[features]
    y = df['Gana_Local']
    
    # Respetamos la línea de tiempo: Entrenamos con el pasado (80%) y evaluamos con el futuro (20%)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
    
    print("🤖 Entrenando XGBoost con hiperparámetros optimizados...")
    modelo = xgb.XGBClassifier(
        n_estimators=200,      # Más árboles de decisión
        learning_rate=0.03,    # Aprendizaje más lento y preciso
        max_depth=5,           # Ligeramente más profundo para captar relaciones entre Pitcher y Racha
        subsample=0.8,         # Previene sobreajuste (overfitting)
        eval_metric='logloss',
        random_state=42
    )
    
    modelo.fit(X_train, y_train)
    
    predicciones = modelo.predict(X_test)
    precision = accuracy_score(y_test, predicciones)
    
    print("-" * 60)
    print(f"🎯 Precisión del Cerebro V2: {precision * 100:.2f}%")
    print("-" * 60)
    
    joblib.dump(modelo, 'oraculo_mlb_xgboost.pkl')
    print("💾 Nuevo cerebro instalado. Listo para predecir.")

if __name__ == "__main__":
    entrenar_cerebro_v2()