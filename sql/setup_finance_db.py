"""
setup_finance_db.py
-------------------
Crea un database SQLite fittizio per esercitarsi con SQL in ottica buy-side.

Tabelle:
  funds       - anagrafica dei 10 fondi (+ benchmark di riferimento)
  securities  - anagrafica dei 50 strumenti singoli + gli strumenti benchmark (ETF/indici)
  benchmarks  - mappa ogni benchmark al suo strumento prezzato in `securities`
  prices      - prezzi daily (close) per OGNI security, ~9 mesi di giorni feriali
  holdings    - snapshot MENSILE delle posizioni di ogni fondo (quantita per strumento)
  trades      - operazioni (BUY/SELL) eseguite dai fondi nel periodo

Esecuzione:
    python setup_finance_db.py
Output:
    finance.db  (nella stessa cartella dello script)

Nota didattica: ho aggiunto la tabella `securities` (anagrafica strumenti) che
non era nella tua lista, ma e' indispensabile per fare JOIN puliti. E' la
"dimension table" classica: holdings/prices/trades la referenziano via security_id.
"""

import sqlite3
import os
from datetime import date

import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)  # riproducibile
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "finance.db")

# ---------------------------------------------------------------------------
# 1) PARAMETRI DI BASE
# ---------------------------------------------------------------------------
START = date(2025, 9, 1)
END = date(2026, 5, 29)          # ~9 mesi -> ben oltre i 6 mesi richiesti

# 5 benchmark (ETF / indici) che verranno prezzati come "securities"
BENCHMARKS = [
    # ticker,        name,                          asset_class
    ("SPX",  "S&P 500 Index",                  "Index"),
    ("SX5E", "EURO STOXX 50 Index",            "Index"),
    ("IEUR", "iShares Core MSCI Europe ETF",   "ETF"),
    ("AGG",  "iShares Core Euro Govt Bond ETF","ETF"),
    ("ACWI", "MSCI All-Country World ETF",     "ETF"),
]

FUND_STRATEGIES = [
    ("Eurizon European Equity",      "Equity Europe",   "EUR", "SX5E"),
    ("Anima Global Growth",          "Equity Global",   "EUR", "ACWI"),
    ("Fideuram US Equity",           "Equity US",       "USD", "SPX"),
    ("Mediolanum Euro Bond",         "Fixed Income",    "EUR", "AGG"),
    ("Generali Balanced Income",     "Balanced",        "EUR", "IEUR"),
    ("AXA IM Tech Leaders",          "Equity Sector",   "USD", "SPX"),
    ("Azimut Energy & Utilities",    "Equity Sector",   "EUR", "SX5E"),
    ("Banca Generali Dividend",      "Equity Income",   "EUR", "IEUR"),
    ("Eurizon Pharma & Health",      "Equity Sector",   "EUR", "IEUR"),
    ("Anima Defensive Allocation",   "Balanced",        "EUR", "AGG"),
]

# ---------------------------------------------------------------------------
# 2) ANAGRAFICA STRUMENTI (50 singoli)
# ---------------------------------------------------------------------------
TICKER_POOL = {
    "Energy":      ["XOM", "CVX", "SHEL", "TTE", "ENI", "BP", "EQNR"],
    "Banks":       ["JPM", "BAC", "ISP", "UCG", "BNP", "SAN", "DBK"],
    "Tech":        ["AAPL", "MSFT", "NVDA", "ASML", "SAP", "STM", "ADBE"],
    "Pharma":      ["PFE", "JNJ", "NOVN", "SANP", "AZN", "RHHBY", "GSK"],
    "Consumer":    ["KO", "PG", "NKE", "MC", "OR", "ITX"],
    "Utilities":   ["NEE", "ENEL", "IBE", "EOAN", "RWE"],
    "Industrials": ["GE", "SIE", "AIR", "CAT", "DHR"],
    "Telecom":     ["VZ", "T", "DTE", "TEF", "TIT"],
}

USD_TICKERS = {"XOM", "CVX", "JPM", "BAC", "AAPL", "MSFT", "NVDA", "ADBE",
               "PFE", "JNJ", "KO", "PG", "NKE", "NEE", "GE", "CAT", "DHR",
               "VZ", "T", "RHHBY", "AZN", "GSK", "SHEL", "BP"}

securities = []
sec_id = 1
for sector, tickers in TICKER_POOL.items():
    for tk in tickers:
        ccy = "USD" if tk in USD_TICKERS else "EUR"
        securities.append({
            "security_id": sec_id,
            "ticker": tk,
            "security_name": f"{tk} {sector} Corp",
            "sector": sector,
            "asset_class": "Equity",
            "currency": ccy,
            "is_benchmark": 0,
        })
        sec_id += 1

securities = securities[:50]  # esattamente 50 strumenti singoli
sec_id = 51

bench_secid = {}
for tk, name, ac in BENCHMARKS:
    securities.append({
        "security_id": sec_id,
        "ticker": tk,
        "security_name": name,
        "sector": "Benchmark",
        "asset_class": ac,
        "currency": "USD" if tk in ("SPX", "ACWI") else "EUR",
        "is_benchmark": 1,
    })
    bench_secid[tk] = sec_id
    sec_id += 1

df_sec = pd.DataFrame(securities)

# ---------------------------------------------------------------------------
# 3) FONDI + BENCHMARKS
# ---------------------------------------------------------------------------
df_bench = pd.DataFrame([
    {"benchmark_id": i + 1, "benchmark_name": name,
     "ticker": tk, "security_id": bench_secid[tk]}
    for i, (tk, name, ac) in enumerate(BENCHMARKS)
])
bench_id_by_ticker = dict(zip(df_bench["ticker"], df_bench["benchmark_id"]))

funds = []
for i, (name, strat, ccy, bench_tk) in enumerate(FUND_STRATEGIES, start=1):
    inception = date(2018 + (i % 6), ((i * 2) % 12) + 1, 15)
    funds.append({
        "fund_id": i,
        "fund_name": name,
        "strategy": strat,
        "base_ccy": ccy,
        "inception_date": inception.isoformat(),
        "aum_eur": round(float(RNG.uniform(150, 3500)), 1) * 1_000_000,
        "benchmark_id": bench_id_by_ticker[bench_tk],
    })
df_funds = pd.DataFrame(funds)

# ---------------------------------------------------------------------------
# 4) PREZZI DAILY (GBM semplice) per OGNI security
# ---------------------------------------------------------------------------
biz_days = pd.bdate_range(START, END)   # solo giorni feriali

price_rows = []
for _, s in df_sec.iterrows():
    if s["asset_class"] == "Index":
        mu, sigma, p0 = 0.06, 0.012, RNG.uniform(3000, 5000)
    elif s["asset_class"] == "ETF":
        mu, sigma, p0 = 0.05, 0.010, RNG.uniform(40, 120)
    else:  # Equity
        mu, sigma, p0 = RNG.uniform(-0.02, 0.18), RNG.uniform(0.012, 0.030), RNG.uniform(15, 350)

    dt = 1 / 252
    shocks = RNG.normal((mu - 0.5 * sigma**2) * dt, sigma * np.sqrt(dt), len(biz_days))
    path = p0 * np.exp(np.cumsum(shocks))
    for d, px in zip(biz_days, path):
        price_rows.append({
            "price_date": d.date().isoformat(),
            "security_id": int(s["security_id"]),
            "close_price": round(float(px), 4),
        })
df_prices = pd.DataFrame(price_rows)

# ---------------------------------------------------------------------------
# 5) HOLDINGS (snapshot mensili: primo giorno feriale di ogni mese)
# ---------------------------------------------------------------------------
month_starts = pd.bdate_range(START, END, freq="BMS")
single_secs = df_sec[df_sec["is_benchmark"] == 0]["security_id"].tolist()

holding_rows = []
for f in funds:
    fid = f["fund_id"]
    n_hold = int(RNG.integers(8, 16))
    held = RNG.choice(single_secs, size=n_hold, replace=False)
    base_qty = {int(sid): int(RNG.integers(1_000, 50_000)) for sid in held}
    for m in month_starts:
        for sid in held:
            qty = max(0, int(base_qty[int(sid)] * RNG.uniform(0.85, 1.15)))
            holding_rows.append({
                "holding_date": m.date().isoformat(),
                "fund_id": fid,
                "security_id": int(sid),
                "quantity": qty,
            })
df_holdings = pd.DataFrame(holding_rows)

# ---------------------------------------------------------------------------
# 6) TRADES (operazioni sparse nel periodo)
# ---------------------------------------------------------------------------
price_lookup = df_prices.set_index(["security_id", "price_date"])["close_price"].to_dict()
biz_iso = [d.date().isoformat() for d in biz_days]

trade_rows = []
for f in funds:
    fid = f["fund_id"]
    held = df_holdings[df_holdings["fund_id"] == fid]["security_id"].unique().tolist()
    n_trades = int(RNG.integers(20, 41))
    for _ in range(n_trades):
        sid = int(RNG.choice(held))
        d = str(RNG.choice(biz_iso))
        px = price_lookup.get((sid, d))
        if px is None:
            continue
        side = "BUY" if RNG.random() < 0.55 else "SELL"
        qty = int(RNG.integers(100, 10_000))
        trade_rows.append({
            "trade_date": d,
            "fund_id": fid,
            "security_id": sid,
            "side": side,
            "quantity": qty,
            "price": round(float(px), 4),
        })
df_trades = pd.DataFrame(trade_rows).sort_values("trade_date").reset_index(drop=True)
df_trades.insert(0, "trade_id", range(1, len(df_trades) + 1))

# ---------------------------------------------------------------------------
# 7) SCRITTURA SU SQLITE (schema esplicito: PK, FK, tipi)
# ---------------------------------------------------------------------------
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON;")

schema = """
CREATE TABLE securities (
    security_id   INTEGER PRIMARY KEY,
    ticker        TEXT NOT NULL,
    security_name TEXT NOT NULL,
    sector        TEXT NOT NULL,
    asset_class   TEXT NOT NULL,   -- Equity / ETF / Index
    currency      TEXT NOT NULL,
    is_benchmark  INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE benchmarks (
    benchmark_id   INTEGER PRIMARY KEY,
    benchmark_name TEXT NOT NULL,
    ticker         TEXT NOT NULL,
    security_id    INTEGER NOT NULL,
    FOREIGN KEY (security_id) REFERENCES securities(security_id)
);

CREATE TABLE funds (
    fund_id        INTEGER PRIMARY KEY,
    fund_name      TEXT NOT NULL,
    strategy       TEXT NOT NULL,
    base_ccy       TEXT NOT NULL,
    inception_date TEXT NOT NULL,
    aum_eur        REAL NOT NULL,
    benchmark_id   INTEGER NOT NULL,
    FOREIGN KEY (benchmark_id) REFERENCES benchmarks(benchmark_id)
);

CREATE TABLE prices (
    price_date  TEXT NOT NULL,
    security_id INTEGER NOT NULL,
    close_price REAL NOT NULL,
    PRIMARY KEY (price_date, security_id),
    FOREIGN KEY (security_id) REFERENCES securities(security_id)
);

CREATE TABLE holdings (
    holding_date TEXT NOT NULL,
    fund_id      INTEGER NOT NULL,
    security_id  INTEGER NOT NULL,
    quantity     INTEGER NOT NULL,
    PRIMARY KEY (holding_date, fund_id, security_id),
    FOREIGN KEY (fund_id) REFERENCES funds(fund_id),
    FOREIGN KEY (security_id) REFERENCES securities(security_id)
);

CREATE TABLE trades (
    trade_id    INTEGER PRIMARY KEY,
    trade_date  TEXT NOT NULL,
    fund_id     INTEGER NOT NULL,
    security_id INTEGER NOT NULL,
    side        TEXT NOT NULL CHECK (side IN ('BUY','SELL')),
    quantity    INTEGER NOT NULL,
    price       REAL NOT NULL,
    FOREIGN KEY (fund_id) REFERENCES funds(fund_id),
    FOREIGN KEY (security_id) REFERENCES securities(security_id)
);
"""
conn.executescript(schema)

df_sec.to_sql("securities", conn, if_exists="append", index=False)
df_bench.to_sql("benchmarks", conn, if_exists="append", index=False)
df_funds.to_sql("funds", conn, if_exists="append", index=False)
df_prices.to_sql("prices", conn, if_exists="append", index=False)
df_holdings.to_sql("holdings", conn, if_exists="append", index=False)
df_trades.to_sql("trades", conn, if_exists="append", index=False)

conn.executescript("""
CREATE INDEX idx_prices_sec    ON prices(security_id);
CREATE INDEX idx_holdings_fund ON holdings(fund_id);
CREATE INDEX idx_trades_fund   ON trades(fund_id);
CREATE INDEX idx_trades_sec    ON trades(security_id);
""")
conn.commit()

# ---------------------------------------------------------------------------
# 8) REPORT DI CONTROLLO
# ---------------------------------------------------------------------------
print(f"DB creato: {DB_PATH}\n")
for t in ["funds", "securities", "benchmarks", "prices", "holdings", "trades"]:
    n = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    print(f"  {t:12s}: {n:>7,} righe")

dmin, dmax = conn.execute("SELECT MIN(price_date), MAX(price_date) FROM prices").fetchone()
print(f"\n  range prezzi: {dmin} -> {dmax}")
print("  settori     :", [r[0] for r in conn.execute(
    "SELECT DISTINCT sector FROM securities ORDER BY sector").fetchall()])
conn.close()
