import sqlite3
import os

def configurar_base_datos():
    # Conectar a la base de datos (la crea si no existe)
    conexion = sqlite3.connect('paper_trading.db')
    cursor = conexion.cursor()

    # Crear la tabla de apuestas virtuales
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS virtual_bets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            partido TEXT,
            prediccion TEXT,
            cuota_ofrecida REAL,
            inversion_virtual_cop REAL,
            estado TEXT
        )
    ''')
    
    # Guardar los cambios y cerrar
    conexion.commit()
    conexion.close()
    print("✅ Base de datos 'paper_trading.db' creada exitosamente.")

# Esta línea le dice a Python que ejecute la función cuando corramos el archivo
if __name__ == "__main__":
    configurar_base_datos()