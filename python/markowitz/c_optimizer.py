import pandas as pd
import numpy as np
from scipy.optimize import minimize

def compute_stats(rend: pd.DataFrame) -> tuple[pd.Series, pd.DataFrame]:
    """Calcola i rendimenti medi e la matrice varianza-covarianza annualizzati"""

    mu = rend.mean()*252
    Sigma = rend.cov()*252

    return (mu, Sigma)



def min_variance_ptf(mu:pd.Series, Sigma:pd.DataFrame) -> np.ndarray:
    """Calcola il ptf a varianza minima"""

    N = len(mu)
    w0 = np.ones(N)/N # Pesi iniziali= ptf omogeneo
    def obiettivo(w): return w@Sigma@w # Funzione obiettivo: varianza del ptf
    boundaries = [(0,1)]*N # Limito i pesi ad essere solamente positivi
    constr = {"type":"eq", "fun": lambda x: x.sum()-1} # Richiedo che i pesi sommino a 1
    w = minimize(fun= obiettivo, bounds= boundaries, constraints= constr, method="SLSQP", x0=w0, options={"ftol": 1e-12}) # Minimizzo la funzione

    if not w.success: # Flag per errore di convergenza
        print("Errore di convergenza")
        return 0

    w.x = np.where(w.x < 1e-6, 0, w.x) # I pesi troppo piccoli vengono impostati a 0

    return w.x



def max_sharpe(mu:pd.Series, Sigma:pd.DataFrame, rf: float) -> np.ndarray:
    """Calcola il ptf con massimo sharpe ratio (pft Tangente)"""

    N = len(mu)
    w0 = np.ones(N)/N # Pesi iniziali= ptf omogeneo
    def obiettivo(w): return -(w@mu - rf)/np.sqrt(w@Sigma@w) # Funzione obiettivo: sharpe ratio del ptf (col - perchè uso minimize ma mi serve il suo valore massimo)
    boundaries = [(0,1)]*N # Limito i pesi ad essere solamente positivi
    constr = {"type":"eq", "fun": lambda x: x.sum()-1} # Richiedo che i pesi sommino a 1
    w = minimize(fun= obiettivo, bounds= boundaries, constraints= constr, method="SLSQP", x0=w0, options={"ftol": 1e-12}) # Minimizzo la funzione
    
    if not w.success: # Flag per errore di convergenza
        print("Errore di convergenza")
        return 0

    w.x = np.where(w.x < 1e-6, 0, w.x)  # I pesi troppo piccoli vengono impostati a 0

    return w.x



def efficient_frontier(mu:pd.Series, Sigma:pd.DataFrame, n_points:int) -> list:
    """Calcola la frontiera efficiente degli n_points portafogli aventi rendimenti tra mu_MVP e mu_max"""
    min_var_ptf = min_variance_ptf(mu,Sigma)@mu 
    points = np.linspace(min_var_ptf, np.max(mu), n_points) # Seleziono le medie obiettivo per la frontiera
    frontier = [] 

    N = len(mu) 
    w0 = np.ones(N)/N # Pesi iniziali= ptf omogeneo
    def obiettivo(w): return w@Sigma@w # Funzione obiettivo: varianza del ptf
    boundaries = [(0,1)]*N # Limito i pesi ad essere solamente positivi

    for aim in points: # per ogni media all'interno del vettore, trovo il ptf a var minima che la ottenga
        constr = [{"type":"eq", "fun": lambda x: x.sum()-1}, # Richiedo che i pesi sommino a 1
                    {"type":"eq", "fun": lambda x, t= aim: x@mu-t}] # Richiedo che la media del ptf sia uguale a quella che sto cercando
        w = minimize(fun= obiettivo, bounds= boundaries, constraints= constr, method="SLSQP", x0=w0, options={"ftol": 1e-12}) # Minimizzo la funzione

        if not w.success: # Flag per errore di convergenza
            print("Errore di convergenza")
            return 0

        w.x = np.where(w.x < 1e-6, 0, w.x) # I pesi troppo piccoli vengono impostati a 0
        frontier.append(w.x) 
        
    return frontier



# if __name__ == "__main__":
#     from a_data import get_returns, tickers, info, start, end
#     from b_screening import screen_ticker
    
#     rend = get_returns(tickers, start, end)
#     rend_ok, score = screen_ticker(rend, info, n=20)
    
#     mu, Sigma = compute_stats(rend_ok)
#     w_gmv = min_variance_ptf(mu, Sigma)
#     w_tg = max_sharpe(mu, Sigma, rf=0.04)
#     frontier = efficient_frontier(mu, Sigma, n_points=50)
    
#     print(f"GMV weights:\n{pd.Series(w_gmv, index=rend_ok.columns)}")
#     print(f"\nTangency weights:\n{pd.Series(w_tg, index=rend_ok.columns)}")
#     print(f"\nFrontier points: {len(frontier)}")