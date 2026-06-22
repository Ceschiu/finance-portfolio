import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt

def plot_frontier(frontier: list, w_gmv: np.ndarray, w_tg: np.ndarray, mu: pd.Series, Sigma: pd.DataFrame, tickers: list):
    """Print il grafico della frontiera dei ptf con ptf tangente e ptf a minima varianza + Print grafico risultati single name"""

    fig, ax = plt.subplots() # creo il primo plot 
    for w in frontier: # per ogni punto della frontiera calcolo rendimento, vol e lo inserisco
        media = w@mu
        vol = np.sqrt(w@Sigma@w)
        ax.scatter(vol, media, s = 5, color= "Black")

    mvp_mu = w_gmv@mu # calcolo e inserisco il ptf MV
    mvp_vol = np.sqrt(w_gmv@Sigma@w_gmv)
    ax.scatter(mvp_vol, mvp_mu, s=15, color= "Red")
    ax.annotate("MVP", xy=(mvp_vol,mvp_mu))

    tg_mu = w_tg@mu # calcolo e inserisco il ptf Tg
    tg_vol = np.sqrt(w_tg@Sigma@w_tg)
    ax.scatter(tg_vol, tg_mu, s=15, color= "Blue")
    ax.annotate("TGP", xy=(tg_vol,tg_mu))
    
    base = os.path.dirname(__file__) # Salvo plot
    path = os.path.join(base, "Frontiera.png")
    plt.savefig(path, dpi = 150, bbox_inches="tight")

    fig, ax = plt.subplots() # creo il secondo plot 
    for ticker in tickers: # per ogni ticker inserisco il punto nel grafico 
        ax.scatter(np.sqrt(Sigma[ticker].loc[ticker]), mu[ticker], s = 10)
        ax.annotate(ticker, xy=(np.sqrt(Sigma[ticker].loc[ticker]), mu[ticker]))

    path = os.path.join(base, "Scatter_Single_Name.png")
    plt.savefig(path, dpi = 150, bbox_inches="tight")
    return

def print_weights(w: np.ndarray, tickers: list, name: str):
    """Stampa in maniera ordinata i pesi del ptf name"""
    df = pd.DataFrame(index = tickers, data ={"peso": w})
    df = df[df["peso"]>0]
    print(f"=== {name} === \n {df['peso'].map('{:.1%}'.format)}")
    return

# if __name__ == "__main__":
#     from a_data import get_returns, tickers, info, start, end
#     from b_screening import screen_ticker
#     from c_optimizer import compute_stats, min_variance_ptf, max_sharpe, efficient_frontier

#     rend = get_returns(tickers, start, end)
#     rend_ok, score = screen_ticker(rend, info, n=20)
#     mu, Sigma = compute_stats(rend_ok)
#     w_gmv = min_variance_ptf(mu, Sigma)
#     w_tg = max_sharpe(mu, Sigma, rf=0.04)
#     frontier = efficient_frontier(mu, Sigma, n_points=50)

#     plot_frontier(frontier, w_gmv, w_tg, mu, Sigma, list(rend_ok.columns))
#     print_weights(w_gmv, list(rend_ok.columns), "GMV Portfolio")
#     print_weights(w_tg, list(rend_ok.columns), "Tangency Portfolio")
