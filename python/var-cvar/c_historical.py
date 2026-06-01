import pandas as pd
import numpy as np

def VaR_Historical(w:pd.Series, rend:pd.DataFrame, alpha:float = 0.95) -> tuple[float,float]:
    """Calcola il VaR e l'ES annualizzati di un portafoglio, utilizzando l'Historical Simulation"""
    # Calcolo rendimenti storici del ptf
    rend_ptf = rend@w

    # Calcolo VaR e ES del ptf con confidenza alpha
    VaR = -rend_ptf.quantile(1-alpha)
    ES = -rend_ptf[rend_ptf< -VaR].mean()
    
    # Metodo meno veloce
    # rend_ptf = np.sort_values(rend_ptf)
    # n = int(np.floor((1-alpha)*len(rend_ptf)))
    # ES = -np.sum(rend_ptf.iloc[:n])/n

    return (VaR,ES)