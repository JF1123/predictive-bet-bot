import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

def preparar_datos_y_entrenar():
    print("🧠 INICIANDO ENTRENAMIENTO DEL MODELO ORÁCULO...")
    
    # 1. Cargar los datos que descargamos previamente
    url = "https://www.football-data.co.uk/mmz4281/2324/E0.csv"
    df = pd.read_csv(url)
    
    # Limpiamos datos vacíos por si acaso
    df = df.dropna(subset=['FTHG', 'FTAG', 'B365H', 'B365D', 'B365A'])
    
    # 2. CREAR LA VARIABLE OBJETIVO (Y)
    # Si Goles Local > Goles Visitante = 1
    # Si Goles Local == Goles Visitante = 0 (Empate)
    # Si Goles Local < Goles Visitante = 2
    def determinar_resultado(fila):
        if fila['FTHG'] > fila['FTAG']: return 1
        elif fila['FTHG'] == fila['FTAG']: return 0
        else: return 2
        
    df['Resultado_Real'] = df.apply(determinar_resultado, axis=1)
    
    # 3. CREAR LAS CARACTERÍSTICAS (X)
    # Convertimos las cuotas históricas en probabilidades implícitas (1 / cuota)
    df['Prob_Impl_Local'] = 1 / df['B365H']
    df['Prob_Impl_Empate'] = 1 / df['B365D']
    df['Prob_Impl_Visitante'] = 1 / df['B365A']
    
    # Definimos qué columnas usará el modelo para "estudiar"
    X = df[['Prob_Impl_Local', 'Prob_Impl_Empate', 'Prob_Impl_Visitante']]
    y = df['Resultado_Real']
    
    # 4. DIVIDIR LOS DATOS (80% para estudiar, 20% para hacerle un examen sorpresa)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 5. ENTRENAR EL MODELO (Random Forest)
    print("📚 El modelo está estudiando el historial...")
    modelo = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    modelo.fit(X_train, y_train)
    
    # 6. EVALUAR EL MODELO (El Examen)
    predicciones = modelo.predict(X_test)
    precision = accuracy_score(y_test, predicciones)
    
    print("\n✅ ¡ENTRENAMIENTO COMPLETADO!")
    print(f"🎯 Precisión del modelo en partidos no vistos: {precision * 100:.2f}%")
    
    print("\n📊 Desglose del rendimiento por categoría (1=Local, 0=Empate, 2=Visitante):")
    print(classification_report(y_test, predicciones, zero_division=0))

if __name__ == "__main__":
    preparar_datos_y_entrenar()