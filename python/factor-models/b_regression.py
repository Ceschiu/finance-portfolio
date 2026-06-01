import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.regression.linear_model import RegressionResultsWrapper


def CAPM_calc(rend_monthly: pd.DataFrame, weights: pd.Series, ff: pd.DataFrame) -> RegressionResultsWrapper:
    """Calcola il risultato di una regressione OLS secondo il modello CAPM"""

    rf = ff["RF"] # Risk free rate from ff_factors
    X = ff["Mkt-RF"] # Mkt excess
    rend_ptf = rend_monthly@weights
    y = rend_ptf - rf # asset excess

    model = sm.OLS(y, sm.add_constant(X)) # OLS: y = beta*mkt_coeff + alpha
    result = model.fit()
    
    return result

def FF3_calc(rend_monthly: pd.DataFrame, weights: pd.Series, ff: pd.DataFrame) -> RegressionResultsWrapper:
    """Calcola il risultato di una regressione OLS secondo il modello FF a 3 fattori"""
    
    rf = ff["RF"] # Risk free rate from ff_factors
    e_mkt = ff["Mkt-RF"] # Mkt excess
    smb = ff["SMB"] # Small minus Big
    hml = ff["HML"] # High minus Low
    X = pd.DataFrame({"Mkt-RF": e_mkt, "SMB": smb, "HML": hml}) # Multi vector df
    X = sm.add_constant(X)

    rend_ptf = rend_monthly@weights
    y = rend_ptf - rf # asset excess
    result = sm.OLS(y, X).fit()

    return result

def FF5_calc(rend_monthly: pd.DataFrame, weights: pd.Series, ff: pd.DataFrame) -> RegressionResultsWrapper:
    """Calcola il risultato di una regressione OLS secondo il modello FF a 5 fattori"""
    
    rf = ff["RF"] # Risk free rate from ff_factors
    e_mkt = ff["Mkt-RF"] # Mkt excess
    smb = ff["SMB"] # Small minus Big
    hml = ff["HML"] # High minus Low
    rmw = ff["RMW"] # Robustness Minus Weak
    cma = ff["CMA"] # Conservative Minus Aggressive 

    X = pd.DataFrame({"Mkt-RF": e_mkt, "SMB": smb, "HML": hml, "RMW": rmw, "CMA": cma}) # Multi vector df
    X = sm.add_constant(X)

    rend_ptf = rend_monthly@weights
    y = rend_ptf - rf # asset excess 
    result = sm.OLS(y, X).fit()

    return result