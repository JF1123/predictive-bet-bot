import pandas as pd
import os

def analizar_super_dataset():
    carpeta_datos = "Club-Football-Match-Data-2000-2025/data"
    
    # 1. Verificamos qué archivos existen realmente en la carpeta
    if not os.path.exists(carpeta_datos):
        print(f"❌ Error: No se encontró la carpeta {carpeta_datos}.")
        return
        
    archivos_reales = os.listdir(carpeta_datos)
    print(f"🔍 Archivos detectados en la carpeta: {archivos_reales}")
    
    # 2. Buscamos automáticamente el archivo correcto
    ruta_archivo = None
    for archivo in archivos_reales:
        if "match" in archivo.lower() and archivo.endswith(".csv"):
            ruta_archivo = os.path.join(carpeta_datos, archivo)
            break
            
    if not ruta_archivo:
        print("❌ Error: No se pudo encontrar ningún archivo de partidos (.csv).")
        return
        
    print(f"📂 Archivo objetivo encontrado: {ruta_archivo}")
    print("⏳ Cargando datos en la memoria RAM... (Esto puede tomar unos segundos)")
    
    # 3. Leemos el archivo
    df = pd.read_csv(ruta_archivo, low_memory=False)
    
    print("✅ ¡Carga completada!")
    print(f"📊 Total de Partidos: {len(df):,}")
    print(f"📅 Rango de tiempo: Desde {df['MatchDate'].min()} hasta {df['MatchDate'].max()}")
    
    ligas = df['Division'].unique()
    print(f"🏆 Número de Ligas distintas: {len(ligas)}")
    
    # Imprimimos las variables más valiosas
    columnas_oro = ['MatchDate', 'HomeTeam', 'AwayTeam', 'HomeElo', 'AwayElo', 'OddHome']
    columnas_presentes = [col for col in columnas_oro if col in df.columns]
    
    print("\n--- MUESTRA DE LA MATRIZ DE ENTRENAMIENTO ---")
    print(df[columnas_presentes].tail())

if __name__ == "__main__":
    analizar_super_dataset()