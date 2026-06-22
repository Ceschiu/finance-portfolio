import pandas as pd
import numpy as np

def screen_ticker(prices: pd.DataFrame, n:int, NaN_treshold: float = 0.05, drawdown_treshold: float = -0.6, vol_treshold: float = 0.5, verbose: bool = False) -> tuple[list, pd.DataFrame]:
    """Screen tickers universe and return top n by composite score and their final score"""
    prices_filtered = prices.copy() # copy in order not to change the original df
    NaN_counter = prices.isna().sum() # Count NaN values and clear
    for ticker in prices_filtered.columns:
        if NaN_counter[ticker] > NaN_treshold*len(prices):
            prices_filtered = prices_filtered.drop(columns= ticker)
            if verbose: # Stampa se richiesto il perchè elimino i ticker
                print(f"Eliminato {ticker} poichè presenta {NaN_counter[ticker]/len(prices):.2%} NaN")

    prices_filtered = prices_filtered.ffill() # Fill the NaN with the previous valid value
    rend_filtered = pd.DataFrame(np.log(prices_filtered/prices_filtered.shift(1)).dropna()) # Compute log returns for the filtered tickers  

    vol = rend_filtered.std()*np.sqrt(252) # Coumpute vol

    prezzi_cumulati = (1+rend_filtered).cumprod() # Coumpute max_drawdown
    max_rolling = prezzi_cumulati.cummax()
    max_drawdown = (prezzi_cumulati/max_rolling -1).min()

    for ticker in rend_filtered.columns: # Clear wrt vol and max_drawdown
        if (vol[ticker]>vol_treshold) or (max_drawdown[ticker] < drawdown_treshold):
            rend_filtered = rend_filtered.drop(columns= ticker)
            if verbose: # Stampa se richiesto il perchè elimino i ticker
                if vol[ticker]>vol_treshold: 
                    print(f"Eliminato {ticker} poichè presenta volatilità pari a {vol[ticker]:.2%} superiore a {vol_treshold}")
                else:
                    print(f"Eliminato {ticker} poichè presenta Max_Drawdown pari a {max_drawdown[ticker]:.4f} superiore a {drawdown_treshold}")

    score_df = pd.DataFrame(index = rend_filtered.columns, columns=["sharpe", "score_sharpe", "corr_mean", "score_corr", "score_SharpeCorr"])
    score_df["sharpe"] = rend_filtered.apply(lambda x: x.mean()*252/(x.std()*np.sqrt(252))) # Sharpe score
    score_df["score_sharpe"] = score_df["sharpe"].rank(ascending = True)
    score_df["corr_mean"] = rend_filtered.corr().mean(axis = 1) # Corr score
    score_df["score_corr"] = score_df["corr_mean"].rank(ascending = False)
    score_df["score_SharpeCorr"] = score_df["score_sharpe"]+score_df["score_corr"] #Total Score

    score_df = score_df.sort_values(by=["score_SharpeCorr","sharpe"], ascending = [False,False]) # Ordino in maniera da avere prima quelli con miglior cross_score e in caso di paritò miglior sharpe
    if len(score_df)> n: # Se ho un numero di ticker superiore a quanto ricchiesto, prendo i migliori
        for ticker in score_df.index[n:]: # elimino gli ultimi ticker fino ad averne n
            if verbose: # Stampa se richiesto il perchè elimino i ticker
                print(f"Eliminato {ticker} poichè non presente nei primi {n} tickers, possedendo uno Score_Totale= {score_df['score_SharpeCorr'].loc[ticker]}, fatto da Sharpe_Score= {score_df['score_sharpe'].loc[ticker]} e Corr_Score ={score_df['score_corr'].loc[ticker]}")
            score_df = score_df.drop(index = ticker) 
            rend_filtered = rend_filtered.drop(columns=ticker)
            
    return (list(rend_filtered.columns),score_df)



# if __name__ == "__main__":
#     from a_data import get_returns, tickers, info, start, end

#     rend = get_returns(tickers, start, end)
#     rend_ok, score = screen_ticker(rend, info, n=20, verbose=True)
#     print(f"Ticker selezionati: {list(rend_ok.columns)}")
#     print(f"\nScore:\n{score}")
