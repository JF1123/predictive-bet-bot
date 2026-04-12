import sqlite3
import datetime

def registrar_apuesta(partido, prediccion, cuota, inversion=10000):
    # Conectamos a la base de datos que creaste en el paso anterior
    conexion = sqlite3.connect('paper_trading.db')
    cursor = conexion.cursor()
    
    # Obtenemos la fecha de hoy automáticamente
    fecha_hoy = datetime.date.today().strftime("%Y-%m-%d")
    
    # Insertamos los datos matemáticos
    cursor.execute('''
        INSERT INTO virtual_bets (fecha, partido, prediccion, cuota_ofrecida, inversion_virtual_cop, estado)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (fecha_hoy, partido, prediccion, cuota, inversion, 'PENDIENTE'))
    
    conexion.commit()
    conexion.close()
    print(f"✅ Apuesta registrada: {inversion} COP a la opción '{prediccion}' en el partido {partido} (Cuota: {cuota})")

def ver_apuestas():
    # Leemos la base de datos para ver qué hay adentro
    conexion = sqlite3.connect('paper_trading.db')
    cursor = conexion.cursor()
    
    cursor.execute('SELECT * FROM virtual_bets')
    apuestas = cursor.fetchall()
    
    print("\n--- LIBRO MAYOR DE APUESTAS VIRTUALES ---")
    for apuesta in apuestas:
        # Formateamos la salida para que sea fácil de leer en la terminal
        print(f"ID: {apuesta[0]} | Fecha: {apuesta[1]} | Partido: {apuesta[2]} | Predicción: {apuesta[3]} | Cuota: {apuesta[4]} | Monto: {apuesta[5]} | Estado: {apuesta[6]}")
        
    conexion.close()

# Las instrucciones que se ejecutan al correr el archivo
if __name__ == "__main__":
    # 1. Registramos una apuesta de prueba basada en tu imagen
    registrar_apuesta("Once Caldas vs Millonarios", "1 (Gana Local)", 2.28)
    
    # 2. Mostramos el libro mayor en pantalla
    ver_apuestas()
    