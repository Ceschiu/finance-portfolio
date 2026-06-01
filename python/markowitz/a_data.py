import numpy as np
import pandas as pd
import yfinance as yf

def get_prices(tickers: list, start: str, end: str) -> pd.DataFrame:
    """Funzione che ritorna un df di prezzi dei ticker di interesse nella finestra temporale richiesta"""
    data = yf.download(tickers, start= start, end= end)["Close"]
    return data

def get_returns(tickers: list, start: str, end: str) -> pd.DataFrame:
    """Funzione che ritorna un df di log-rendimenti dei ticker di interesse nella finestra temporale richiesta"""
    data = yf.download(tickers, start= start, end= end)["Close"]
    rend = pd.DataFrame(np.log(data/data.shift(1)).dropna())
    return rend

# Selezione dei tickers di interesse
tickers = ["AAPL","MSFT", "GOOGL", "NVDA", "META", "AMZN",
        "JPM", "GS", "BAC", "BLK", 
        "JNJ", "UNH", "PFE", "ABBV",
        "XOM", "CVX", "BP", "SHEL",
        "PG", "KO", "MCD", "NKE",
        "CAT", "HON", "GE",
        "ASML", "SAP", "MC.PA", "NESN.SW", "SIE.DE",
        "GLD", "SLV", "USO",
        "TLT", "BND", "HYG",
        "VNQ", "PLD",
        "NEE", "DUK"]

# Df dei relativi settori di appartenenza
info = pd.DataFrame({
    "ticker": tickers,
    "sector": ["Tech USA","Tech USA", "Tech USA", "Tech USA", "Tech USA", "Tech USA",
        "Finance", "Finance", "Finance", "Finance", 
        "Healthcare", "Healthcare", "Healthcare", "Healthcare",
        "Energy", "Energy", "Energy", "Energy",
        "Consumer", "Consumer", "Consumer", "Consumer",
        "Industriali", "Industriali", "Industriali",
        "Europa", "Europa", "Europa", "Europa", "Europa",
        "Commodities/ETF", "Commodities/ETF", "Commodities/ETF",
        "Bond ETF", "Bond ETF", "Bond ETF",
        "Real Estate", "Real Estate",
        "Utilities", "Utilities"]
})

# Finestra temporale
start="2016-03-31" 
end="2026-03-31"
