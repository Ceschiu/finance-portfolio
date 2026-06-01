import pandas as pd
import numpy as np
import scipy.stats as stats

def VaR_parametric(w:pd.Series, rend:pd.DataFrame, alpha:float = 0.95) -> tuple[float,float]:
    """Calcola il VaR e l'ES di un portafoglio, utilizzando un approccio parametrico e assumento rendimenti normalmente distribuiti"""
    # Calcolo rendimento e volatilità del ptf
    mu = rend.mean()
    mu_ptf = w@mu
    Sigma = rend.cov()
    vol_ptf = np.sqrt(w@Sigma@w)
    
    # Calcolo VaR e ES del ptf con confidenza alpha
    VaR = -(mu_ptf - vol_ptf * stats.norm.ppf(alpha))
    ES = -(mu_ptf - vol_ptf * stats.norm.pdf(stats.norm.ppf(alpha))/(1-alpha))
    
    return (VaR,ES)
    