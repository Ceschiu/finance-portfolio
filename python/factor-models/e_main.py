from a_data import tickers, weights, start, end, get_returns, get_monthly_returns, ff_factors
from b_regression import CAPM_calc, FF3_calc, FF5_calc
from c_attribution import compute_contribution
from d_plotting import plot_factor_analysis

print(f"=========   Inizio   =========")

print(f"=========   Scarico i dati di mercato mensili e i dati del ptf per il calcolo dei log-returns mensili   =========")
rend_monthly = get_monthly_returns(tickers=tickers, start=start, end=end)
ff = ff_factors(start=start, end=end)
rend_monthly, ff = rend_monthly.align(ff, join='inner', axis=0) # nel caso in cui le finestre temporali di ff e rend_monthly non coincidano in partenzza, le allineo

print(f"=========   Calcolo i parametri dei modelli   =========")
capm_result = CAPM_calc(rend_monthly=rend_monthly, weights=weights, ff=ff)
ff3_result = FF3_calc(rend_monthly=rend_monthly, weights=weights, ff=ff)
ff5_result = FF5_calc(rend_monthly=rend_monthly, weights=weights, ff=ff)

print(f"=========   Calcolo le total contribution per ogni modello   =========")
capm_attr = compute_contribution(result=capm_result, ff=ff)
ff3_attr = compute_contribution(result=ff3_result, ff=ff)
ff5_attr = compute_contribution(result=ff5_result, ff=ff)

print(f"=========   Plot delle contribution dei fattori per confronto modelli    =========")
plot_factor_analysis(capm_result=capm_result, ff3_result=ff3_result, ff5_result=ff5_result, capm_attr=capm_attr, ff3_attr=ff3_attr, ff5_attr=ff5_attr, model_selected="ff5")

print(f"=========   Fine   =========")