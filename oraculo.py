import pandas as pd
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import warnings

warnings.filterwarnings('ignore')

def entrenar_oraculo_v2():
    carpeta_datos = "Club-Football-Match-Data-2000-2025/data"
    archivos_reales = os.listdir(carpeta_datos)
    
    ruta_archivo = None
    for archivo in archivos_reales:
        if "match" in archivo.lower() and archivo.endswith(".csv"):
            ruta_archivo = os.path.join(carpeta_datos, archivo)
            break
            
    print("🧠 Cargando el Santo Grial de los datos...")
    df = pd.read_csv(ruta_archivo, low_memory=False)
    
    # 1. NUEVA INGENIERÍA DE CARACTERÍSTICAS
    print("⚙️ Inyectando variables de 'Momento' (Forma de los últimos 5 partidos)...")
    # Agregamos las nuevas variables de racha
    columnas_necesarias = ['HomeElo', 'AwayElo', 'Form5Home', 'Form5Away', 'FTResult']
    
    # Dosis de realidad: En las primeras 5 fechas de cada liga, la "Forma" estará vacía (NaN).
    # Las redes neuronales odian los vacíos. Borramos esas filas.
    df_limpio = df[columnas_necesarias].dropna()
    
    # Matemáticas derivadas
    df_limpio['EloDifference'] = df_limpio['HomeElo'] - df_limpio['AwayElo']
    
    # Nueva variable inventada: ¿Quién tiene mejor racha?
    df_limpio['FormDifference'] = df_limpio['Form5Home'] - df_limpio['Form5Away']
    
    # Matriz de variables independientes (X)
    X = df_limpio[['HomeElo', 'AwayElo', 'EloDifference', 'Form5Home', 'Form5Away', 'FormDifference']]
    y = df_limpio['FTResult'] 
    
    # 2. SEPARACIÓN
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print(f"📚 Partidos para que el modelo estudie: {len(X_train):,}")
    
    # 3. ENTRENAMIENTO
    print("🤖 Entrenando el Bosque Aleatorio 2.0...")
    # max_depth=7: Dejamos que el árbol crezca un poco más porque ahora tiene más variables que analizar
    modelo = RandomForestClassifier(n_estimators=100, max_depth=7, random_state=42)
    modelo.fit(X_train, y_train)
    
    # 4. EVALUACIÓN
    predicciones = modelo.predict(X_test)
    precision = accuracy_score(y_test, predicciones)
    
    print(f"\n✅ ¡Evolución completada!")
    print(f"🎯 Nueva Precisión (Accuracy) global del modelo: {precision * 100:.2f}%")
    
    # 5. AUTOPSIA DEL MODELO (¿Qué está pensando?)
    importancias = modelo.feature_importances_
    print("\n📊 IMPORTANCIA DE LAS VARIABLES (Qué pesos matemáticos le asignó la máquina):")
    for i, col in enumerate(X.columns):
        print(f"- {col}: {importancias[i]*100:.1f}%")

if __name__ == "__main__":
    entrenar_oraculo_v2()