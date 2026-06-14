-- ============================================================
-- 07 - Top 3 posizioni di ogni fondo (ROW_NUMBER)
-- Concetto: top-N per gruppo con ROW_NUMBER() OVER (PARTITION BY)
-- ------------------------------------------------------------
-- Le 3 posizioni piu grandi per valore di mercato di ogni fondo
-- al 2026-05-01.
-- ROW_NUMBER numera le posizioni di ciascun fondo in ordine di
-- valore decrescente; nella query esterna teniamo solo rk <= 3.
-- E' la versione "pulita" dell'argmax: la window function sostituisce
-- la subquery correlata per i "top-N per gruppo".
-- (ROW_NUMBER va in una CTE: non si puo' filtrare nel WHERE.)
-- ============================================================

WITH holding_value AS (
    SELECT f.fund_name, s.ticker, s.sector,
           p.close_price * h.quantity AS pos_value
    FROM funds AS f
    JOIN holdings   AS h ON h.fund_id     = f.fund_id
    JOIN prices     AS p ON p.security_id = h.security_id
                        AND p.price_date  = h.holding_date
    JOIN securities AS s ON s.security_id = h.security_id
    WHERE h.holding_date = '2026-05-01'
),
ranked AS (
    SELECT fund_name, ticker, sector, pos_value,
           ROW_NUMBER() OVER (PARTITION BY fund_name ORDER BY pos_value DESC) AS rk
    FROM holding_value
)
SELECT fund_name, rk, ticker, sector, ROUND(pos_value, 2) AS pos_value
FROM ranked
WHERE rk <= 3
ORDER BY fund_name, rk;
