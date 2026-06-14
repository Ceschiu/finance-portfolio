-- ============================================================
-- 09 - Screen di rischio: i 5 titoli piu volatili
-- Concetto: LAG + aggregazione PER TITOLO (GROUP BY) + top-N
-- ------------------------------------------------------------
-- I 5 titoli con la piu alta volatilita giornaliera sull'intero
-- periodo (esclusi i benchmark): deviazione standard dei rendimenti,
-- rendimento medio e numero di osservazioni.
-- NOTA: qui la volatilita e' UN valore per titolo -> GROUP BY,
-- diverso dalla vol ROLLING della query 06 (un valore per riga via
-- frame). Capire quando serve GROUP BY (un valore per gruppo) vs
-- window+frame (un valore per riga) e' il punto chiave.
-- Deviazione standard a mano: SQRT( media(X^2) - [media(X)]^2 ).
-- ============================================================

WITH rendimenti AS (
    SELECT s.ticker, p.price_date,
           p.close_price
             / LAG(p.close_price) OVER (PARTITION BY p.security_id ORDER BY p.price_date)
             - 1 AS rend
    FROM prices AS p
    JOIN securities AS s ON s.security_id = p.security_id
    WHERE s.is_benchmark = 0
),
stats AS (
    SELECT ticker,
           AVG(rend) AS rend_medio,
           SQRT(AVG(rend * rend) - POWER(AVG(rend), 2)) AS vol,
           COUNT(rend) AS n_oss
    FROM rendimenti
    WHERE rend IS NOT NULL
    GROUP BY ticker
)
SELECT st.ticker, s.sector,
       ROUND(st.rend_medio, 6) AS rend_medio,
       ROUND(st.vol, 6)        AS vol_giornaliera,
       st.n_oss
FROM stats AS st
JOIN securities AS s ON s.ticker = st.ticker
ORDER BY st.vol DESC
LIMIT 5;
