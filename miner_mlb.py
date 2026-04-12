import urllib.request
import zipfile
import os
import pandas as pd

def construir_dataset_mlb():
    print("🏟️ Iniciando el minero de datos de la MLB (Retrosheet)...")
    os.makedirs('mlb_datos', exist_ok=True)
    
    dataframes = []
    
    # Minar las últimas 5 temporadas (2021-2025)
    for year in range(2021, 2026):
        url = f"https://www.retrosheet.org/gamelogs/gl{year}.zip"
        zip_path = f"mlb_datos/gl{year}.zip"
        
        try:
            print(f"📥 Descargando temporada {year}...")
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response, open(zip_path, 'wb') as out_file:
                out_file.write(response.read())
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall('mlb_datos')
            
            # --- EL PARCHE: Búsqueda dinámica del archivo de texto ---
            txt_path = None
            for archivo in os.listdir('mlb_datos'):
                if str(year) in archivo and archivo.lower().endswith('.txt'):
                    txt_path = os.path.join('mlb_datos', archivo)
                    break
            
            if not txt_path:
                print(f"❌ Error: No se encontró el archivo de texto para {year} dentro del ZIP.")
                continue
            # ---------------------------------------------------------

            columnas_indices = [0, 3, 6, 9, 10, 22, 25, 50, 53, 101, 103]
            nombres = [
                'Fecha', 'Visita', 'Local', 'Carreras_Visita', 'Carreras_Local', 
                'Hits_Visita', 'HR_Visita', 'Hits_Local', 'HR_Local', 
                'Pitcher_Visita', 'Pitcher_Local'
            ]
            
            df_year = pd.read_csv(txt_path, header=None, usecols=columnas_indices, names=nombres)
            dataframes.append(df_year)
            print(f"✅ Temporada {year} minada ({len(df_year)} partidos).")
            
        except urllib.error.HTTPError as e:
             if e.code == 404:
                 print(f"⚠️ Aviso: Datos consolidados de {year} aún no disponibles en Retrosheet.")
             else:
                 print(f"❌ Error HTTP al descargar {year}: {e}")
        except Exception as e:
            print(f"❌ Error inesperado en {year}: {e}")
    
    if dataframes:
        print("\n⚙️ Uniendo temporadas y calculando variables objetivo...")
        dataset_final = pd.concat(dataframes, ignore_index=True)
        
        dataset_final['Fecha'] = pd.to_datetime(dataset_final['Fecha'], format='%Y%m%d')
        dataset_final = dataset_final.sort_values(by='Fecha').reset_index(drop=True)
        
        dataset_final['Gana_Local'] = (dataset_final['Carreras_Local'] > dataset_final['Carreras_Visita']).astype(int)
        
        dataset_final.to_csv('mlb_historico.csv', index=False)
        print("-" * 60)
        print("🚀 ¡Minería completada! Archivo 'mlb_historico.csv' guardado en tu servidor.")
        print(f"📊 Total de partidos listos para entrenar: {len(dataset_final)}")
        print("-" * 60)
    else:
        print("❌ Operación fallida. No se descargaron datos.")

if __name__ == "__main__":
    construir_dataset_mlb()