"""
run_query.py — esegue la query scritta in query.sql sul database finance.db
e ne stampa il risultato come tabella.

Uso:
  1. Genera il database:  python setup_finance_db.py
  2. Scrivi la tua query in  query.sql  (nella stessa cartella)
  3. Lancia:  python run_query.py

Richiede pandas.  In alternativa puoi usare un client SQLite
(es. l'estensione SQLTools di VS Code) puntandolo a finance.db.
"""

import os
import sqlite3
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(HERE, "finance.db")
SQL_PATH = os.path.join(HERE, "query.sql")


def main():
    if not os.path.exists(DB_PATH):
        print(f"[!] finance.db non trovato. Esegui prima:  python setup_finance_db.py")
        return
    if not os.path.exists(SQL_PATH):
        print("[i] Crea un file query.sql con la tua query e rilancia.")
        return

    query = open(SQL_PATH, "r", encoding="utf-8").read().strip().rstrip(";").strip()
    if not query:
        print("[i] query.sql e' vuoto.")
        return

    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query(query, conn)
        pd.set_option("display.max_rows", 60)
        pd.set_option("display.max_columns", 30)
        pd.set_option("display.width", 220)
        print(df.to_string(index=False) if not df.empty else "(0 righe)")
        if not df.empty:
            print(f"\n[{len(df)} righe]")
    except Exception as e:
        print("ERRORE SQL:\n  ", e)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
