import pandas as pd
import numpy as np
import yfinance as yf
import os

# Import TgP weights from the folder
base = os.path.dirname(__file__)
TgP = pd.read_csv(os.path.join(base, "TgP_weights.csv"), index_col=0)

# Create the ticker vector for the non-null weights of the TgP 
weights = TgP.iloc[:,0]
weights = weights[weights>0]
tickers = list(weights.index)
# Time window
start = "2016-03-31"
end = "2026-03-31"

def get_returns(tickers: list, start: str, end: str) -> pd.DataFrame:
    """Funzione che ritorna un df di log-rendimenti dei ticker di interesse nella finestra temporale richiesta"""
    data = yf.download(tickers, start= start, end= end)["Close"]
    rend = pd.DataFrame(np.log(data/data.shift(1)).dropna())
    return rend