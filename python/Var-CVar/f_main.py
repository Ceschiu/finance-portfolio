from a_data import weights, tickers, start, end, get_returns
from b_parametric import VaR_parametric
from c_historical import VaR_Historical
from d_montecarlo import VaR_MonteCarlo
from e_plotting import plot_var

print(f"=========   Inizio   =========")

print(f"=========   Scarico i dati del ptf tangente e calcolo i log-returns   =========")
rend = get_returns(tickers=tickers, start=start, end=end)

print(f"=========   Calcolo VaR e ES con metodo Parametrico   =========")
VaR_Param, ES_Param = VaR_parametric(w=weights, rend=rend, alpha= 0.95)

print(f"=========   Calcolo VaR e ES con Historical Simulation   =========")
VaR_Hist, ES_Hist = VaR_Historical(w=weights, rend=rend, alpha= 0.95)

print(f"=========   Calcolo VaR e ES con metodo MonteCarlo   =========")
VaR_MC, ES_MC = VaR_MonteCarlo(w=weights, rend=rend, alpha= 0.95, n_sim=10000)

print(f"=========   Plot VaR e ES sui Rendimenti del Ptf   =========")
plot_var(w=weights, rend=rend, var_param=VaR_Param, es_param=ES_Param, var_hist=VaR_Hist, es_hist=ES_Hist, var_mc=VaR_MC, es_mc=ES_MC, alpha=0.95)

print(f"=========   Fine   =========")
