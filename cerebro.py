def calcular_probabilidad_implicita(cuota):
    """Convierte la cuota de la casa de apuestas en probabilidad"""
    return 1 / cuota

def criterio_de_kelly(prob_modelo, cuota, bankroll_total):
    """
    Calcula exactamente cuánto dinero apostar usando la fórmula de Kelly.
    """
    b = cuota - 1.0  # Ganancia neta
    p = prob_modelo  # Probabilidad de nuestro modelo de ML
    q = 1.0 - p      # Probabilidad de fallar
    
    # Aplicamos la fórmula matemática
    f_star = (b * p - q) / b
    
    # Kelly fraccional (los quants suelen dividir el resultado a la mitad para reducir la volatilidad)
    f_star_suavizado = f_star / 2
    
    # Si la fórmula da negativo, no hay ventaja matemática. Retornamos 0.
    if f_star_suavizado <= 0:
        return 0.0
        
    return bankroll_total * f_star_suavizado

def evaluar_apuesta(partido, cuota_bookie, prob_modelo_ml, bankroll):
    print(f"--- ANALIZANDO: {partido} ---")
    prob_implicita = calcular_probabilidad_implicita(cuota_bookie)
    
    print(f"La casa de apuestas cree que la probabilidad es: {prob_implicita * 100:.1f}% (Cuota {cuota_bookie})")
    print(f"Nuestro modelo de ML predice una probabilidad de: {prob_modelo_ml * 100:.1f}%")
    
    inversion_sugerida = criterio_de_kelly(prob_modelo_ml, cuota_bookie, bankroll)
    
    if inversion_sugerida > 0:
        print(f"✅ VALOR ENCONTRADO. El algoritmo de Kelly sugiere apostar: {inversion_sugerida:.2f} COP")
        # Aquí en el futuro llamaremos a tu archivo ledger.py para registrar la apuesta
    else:
        print(f"❌ NO HAY VALOR. Matemáticamente es una mala inversión. Abortar.")
    print("\n")

if __name__ == "__main__":
    # Supongamos que tenemos 100,000 COP en nuestra cuenta demo
    capital_virtual = 100000 
    
    # Escenario 1: Nuestro modelo es más inteligente que la casa de apuestas
    evaluar_apuesta("Once Caldas vs Millonarios", cuota_bookie=2.28, prob_modelo_ml=0.55, bankroll=capital_virtual)
    
    # Escenario 2: Nuestro modelo sabe que el equipo va a perder, o no hay ventaja
    evaluar_apuesta("Nacional vs Tolima", cuota_bookie=1.80, prob_modelo_ml=0.50, bankroll=capital_virtual)