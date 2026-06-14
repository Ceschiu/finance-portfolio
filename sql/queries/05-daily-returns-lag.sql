-- ============================================================
-- 05 - Rendimento giornaliero di un titolo (window function LAG)
-- Concetto: LAG() OVER (PARTITION BY ... ORDER BY ...)
-- ------------------------------------------------------------
-- Rendimento daily = close / close_del_giorno_prima - 1.
-- LAG prende il prezzo della RIGA PRECEDENTE nell'ordinamento per
-- data: gestisce automaticamente i weekend (riga precedente, non
-- giorno di calendario -1). Il primo giorno non ha precedente -> NULL.
-- Il filtro del NULL va fatto fuori dalla CTE: le window function
-- si calcolano dopo il WHERE, quindi LAG non puo' stare nel WHERE.
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
       ROUND(rend * 100, 4) AS rend_perc
FROM rendimenti
WHERE rend IS NOT NULL
ORDER BY price_date;
