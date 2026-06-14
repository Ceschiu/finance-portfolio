-- ============================================================
-- 02 - Titolo piu economico per ogni settore
-- Concetto: argmin per gruppo via SUBQUERY CORRELATA
-- ------------------------------------------------------------
-- Per ogni settore, il titolo con il close_price piu basso alla
-- data 2026-05-29 (esclusi i benchmark).
-- MIN da' il VALORE minimo; per recuperare LA RIGA (il ticker) che
-- possiede quel minimo serve una subquery correlata che calcola il
-- minimo sullo STESSO settore della riga esterna.
-- ============================================================

SELECT s.sector, s.ticker, p.close_price
FROM securities AS s
JOIN prices AS p ON p.security_id = s.security_id
WHERE p.price_date = '2026-05-29'
  AND s.is_benchmark = 0
  AND p.close_price = (
        SELECT MIN(p2.close_price)
        FROM securities AS s2
        JOIN prices AS p2 ON p2.security_id = s2.security_id
        WHERE p2.price_date = '2026-05-29'
          AND s2.is_benchmark = 0
          AND s2.sector = s.sector   -- correlazione: stesso settore della riga esterna
  )
ORDER BY s.sector;
