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

def get_monthly_returns(tickers: list, start: str, end: str) -> pd.DataFrame:
    """Funzione che ritorna un df di log-rendimenti mensili dei ticker di interesse nella finestra temporale richiesta"""
    data = yf.download(tickers, start= start, end= end)["Close"]
    rend = pd.DataFrame(np.log(data/data.shift(1)).dropna())
    rend_monthly = rend.resample("ME").sum()
    return rend_monthly

def ff_factors(start: str, end: str) -> pd.DataFrame:
    """Funzione che ritorna i Fama-French Factors mensili per i modelli a 3 e 5 variabili per la nostra finestra temporale"""
    ff = pd.read_csv(os.path.join(base, "F-F_Research_Data_5_Factors_2x3.csv"), skiprows=4, index_col=0)
    ff = ff[ff.index.str.strip().str.match(r'^\d{6}$')]
    ff = ff.apply(pd.to_numeric, errors='coerce').dropna()
    ff.index = pd.to_datetime(ff.index.str.strip(), format="%Y%m") + pd.offsets.MonthEnd(0)
    ff = ff / 100
    ff = ff[(ff.index >= start) & (ff.index <= end)]
    return ff


# Metodologia se funziona datareader
# import pandas_datareader.data as web
# def ff_factors(start: str, end: str) -> pd.DataFrame:
#     """Funzione che ritorna i Fama-French Factors per i modelli a 3 e 5 variabili"""
#     ff_factors = web.DataReader("F-F_Research_Data_5_Factors_2x3", "famafrench", start=start, end=end)
#     ff_factors = ff_factors[0]/100
#     ff_factors.index = ff_factors.index.to_timestamp(how="end")
#     return ff_factors