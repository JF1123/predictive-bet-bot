import pandas as pd
import os

def ver_planilla():
    archivo = 'ledger_simulacion.csv'
    
    if not os.path.exists(archivo):
        print("❌ La bóveda está vacía. El Enjambre no ha registrado ninguna apuesta aún.")
        return

    df = pd.read_csv(archivo)

    print("\n" + "="*55)
    print("📊 PLANILLA DE RENDIMIENTO VIRTUAL (PAPER TRADING)")
    print("="*55)

    # Cálculos principales
    total_invertido = df['Inversion_COP'].sum()
    balance_neto = df['Beneficio_Neto'].sum()
    roi = (balance_neto / total_invertido) * 100 if total_invertido > 0 else 0.0
    
    ganadas = len(df[df['Estado'] == 'Ganada'])
    perdidas = len(df[df['Estado'] == 'Perdida'])
    pendientes = len(df[df['Estado'] == 'Pendiente'])

    print(f"🏦 Capital Inicial (Virtual):  20000.00") # Lo ajustaremos a COP después
    print(f"💵 Total Invertido:          {total_invertido:.2f}")
    print(f"💰 Balance Neto (Pérdida/Ganancia): {balance_neto:+.2f}")
    print(f"📈 ROI (Retorno de Inversión): {roi:.2f}%")
    print("-" * 55)
    print(f"✅ Aciertos:   {ganadas}")
    print(f"❌ Fallos:     {perdidas}")
    print(f"⏳ Pendientes: {pendientes}")
    print("="*55 + "\n")

    if pendientes > 0:
        print("📝 OPERACIONES PENDIENTES EN EL MERCADO:")
        pendientes_df = df[df['Estado'] == 'Pendiente']
        for _, fila in pendientes_df.iterrows():
            print(f"  ▶ {fila['Apuesta_A']} (Cuota: {fila['Cuota']}) | Inversión: {fila['Inversion_COP']:.2f}")
        print("\n")

if __name__ == "__main__":
    ver_planilla()