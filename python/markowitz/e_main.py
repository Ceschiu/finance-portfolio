from a_data import tickers, info, start, end, get_returns, get_prices
from b_screening import screen_ticker
from c_optimizer import compute_stats, min_variance_ptf, max_sharpe, efficient_frontier
from d_plotting import plot_frontier, print_weights
import pandas as pd
import os

print(f"=========   Inizio   =========")

print(f"=========   Scarico i prezzi di tutti i ticker   =========")
prices = get_prices(tickers=tickers, start=start, end=end)

print(f"=========   Pulisco il Db   =========")
selected_tickers, score = screen_ticker(prices=prices, info=info, n=20, NaN_treshold=0.05, drawdown_treshold=-0.6, vol_treshold=0.5, verbose=True)

print(f"=========   Scarico i dati e calcolo i log-returns dei Ticker selezionati   =========")
rend = get_returns(tickers= selected_tickers, start=start, end=end)

print(f"=========   Calcolo rendimento e volatlità anualizzati   =========")
mu, Sigma = compute_stats(rend=rend)

print(f"=========   Calcolo MVP   =========")
MVP = min_variance_ptf(mu=mu, Sigma=Sigma)
print_weights(w=MVP, tickers=list(rend.columns), name="MVP")

print(f"=========   Calcolo TgP   =========")
TgP = max_sharpe(mu=mu, Sigma=Sigma, rf=0.04)
print_weights(w=TgP, tickers=list(rend.columns), name="TgP")

print(f"=========   Calcolo Frontiera Eff   =========")
frontier = efficient_frontier(mu=mu, Sigma=Sigma, n_points=100)

print(f"=========   Plot Frontiera   =========")
plot_frontier(frontier=frontier, w_gmv=MVP, w_tg=TgP, mu=mu, Sigma=Sigma, tickers=list(rend.columns))

print(f"=========   Salvo TgP per VaR,ES e CAPM,FF   =========")
base = os.path.dirname(__file__)
pd.Series(TgP, index = rend.columns).to_csv(os.path.join(base, "../VaR-ES/TgP_weights.csv"))
pd.Series(TgP, index = rend.columns).to_csv(os.path.join(base, "../Factor_Model/TgP_weights.csv"))

print(f"=========   Fine   =========")