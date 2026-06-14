-- ============================================================
-- 06 - Volatilita e media rolling a 20 giorni (frame)
-- Concetto: window function con FRAME (ROWS BETWEEN ...)
-- ------------------------------------------------------------
-- Media mobile e deviazione standard dei rendimenti sulle ultime
-- 20 osservazioni (finestra mobile riga per riga).
-- Il FRAME 'ROWS BETWEEN 19 PRECEDING AND CURRENT ROW' definisce la
-- finestra delle ultime 20 righe.
-- SQLite base non ha STDDEV: la calcoliamo a mano con l'identita
-- della varianza:  Var = media(X^2) - [media(X)]^2,  poi SQRT.
-- ============================================================

WITH rendimenti AS (
    SELECT price_date,
           close_price
             / LAG(close_price) OVER (PARTITION BY security_id ORDER BY price_date)
             - 1 AS rend
    FROM prices
    WHERE security_id = 1
)
SELECT price_date,
       ROUND(rend * 100, 4) AS rend_perc,
       ROUND(AVG(rend) OVER w * 100, 4) AS media_rolling_20,
       ROUND(SQRT(AVG(rend * rend) OVER w - POWER(AVG(rend) OVER w, 2)) * 100, 2) AS vol_rolling_20
FROM rendimenti
WHERE rend IS NOT NULL
WINDOW w AS (ORDER BY price_date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW)
ORDER BY price_date;
