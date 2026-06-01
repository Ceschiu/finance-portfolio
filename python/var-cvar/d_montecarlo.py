import pandas as pd
import numpy as np

def VaR_MonteCarlo(w:pd.Series, rend:pd.DataFrame, alpha:float = 0.95, n_sim:int = 10000) -> tuple[float,float]:
    """Calcola il VaR e l'ES annualizzati di un portafoglio, utilizzando una simulazione MC e assumento rendimenti normalmente distribuiti"""
    # Calcolo rendimento e volatilità del ptf
    mu = rend.mean()
    Sigma = rend.cov()
    rend_sim = np.random.multivariate_normal(mean=mu, cov=Sigma, size=n_sim)
    rend_ptf = rend_sim@w
    
    # Calcolo VaR e ES del ptf con confidenza alpha
    VaR = -np.percentile(rend_ptf,(1-alpha)*100)
    ES = -rend_ptf[rend_ptf< -VaR].mean()
    
    return (VaR,ES)