import sqlite3
import datetime
import cerebro
# Nota: En un entorno real, aquí importaríamos recolector.py para sacar los datos de internet.
# Por ahora, simularemos la matriz de partidos del día.

def obtener_partidos_del_dia():
    """Simula la recolección masiva de partidos de una plataforma"""
    return [
        {"partido": "Once Caldas vs Millonarios", "cuota_1": 2.28, "prob_ml_1": 0.55},
        {"partido": "Nacional vs Tolima", "cuota_1": 1.80, "prob_ml_1": 0.50},
        {"partido": "America de Cali vs Santa Fe", "cuota_1": 2.10, "prob_ml_1": 0.49},
        {"partido": "Bucaramanga vs Pereira", "cuota_1": 2.60, "prob_ml_1": 0.42},
        {"partido": "Junior vs Medellin", "cuota_1": 1.95, "prob_ml_1": 0.60} # Aquí hay una clara ventaja
    ]

def guardar_apuesta_en_bd(partido, cuota, inversion):
    """Conecta con nuestro Libro Mayor para guardar la decisión"""
    conexion = sqlite3.connect('paper_trading.db')
    cursor = conexion.cursor()
    fecha_hoy = datetime.date.today().strftime("%Y-%m-%d")
    
    cursor.execute('''
        INSERT INTO virtual_bets (fecha, partido, prediccion, cuota_ofrecida, inversion_virtual_cop, estado)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (fecha_hoy, partido, "1 (Local)", cuota, inversion, 'PENDIENTE'))
    
    conexion.commit()
    conexion.close()

def ejecutar_pipeline_diario():
    print("🚀 INICIANDO ANÁLISIS MASIVO DE PARTIDOS...\n")
    capital_disponible = 1000000 # 1 millón de pesos virtuales
    
    partidos = obtener_partidos_del_dia()
    apuestas_realizadas = 0
    
    for p in partidos:
        nombre = p["partido"]
        cuota = p["cuota_1"]
        prob_modelo = p["prob_ml_1"]
        
        # 1. El Cerebro evalúa usando el Criterio de Kelly
        inversion = cerebro.criterio_de_kelly(prob_modelo, cuota, capital_disponible)
        
        # 2. Si Kelly dice que hay valor matemático (inversión > 0)
        if inversion > 0:
            print(f"✅ VALOR DETECTADO en {nombre}. Inversión Kelly: {inversion:.2f} COP")
            guardar_apuesta_en_bd(nombre, cuota, inversion)
            capital_disponible -= inversion # Restamos el dinero invertido
            apuestas_realizadas += 1
        else:
            print(f"❌ DESCARTADO: {nombre}. No hay ventaja matemática.")
            
    print(f"\n📊 RESUMEN: Se analizaron {len(partidos)} partidos. Se realizaron {apuestas_realizadas} inversiones virtuales.")
    print("Todas las apuestas están en estado PENDIENTE en tu paper_trading.db")

if __name__ == "__main__":
    ejecutar_pipeline_diario()