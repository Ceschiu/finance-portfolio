-- ============================================================
-- 08 - Rendimento attivo: titolo vs benchmark
-- Concetto: LAG su piu titoli + SELF-JOIN per allineare le date
-- ------------------------------------------------------------
-- Rendimento giornaliero di AAPL e del benchmark SPX, e la loro
-- differenza (rendimento attivo = quanto il titolo fa meglio/peggio
-- dell'indice).
-- I rendimenti dei due titoli si calcolano con LAG PARTITION BY
-- security_id (la partizione evita che il LAG sconfini da un titolo
-- all'altro). Poi un self-join della CTE allinea i due titoli sulla
-- stessa data, per poterne fare la differenza.
-- ============================================================

WITH rendimenti AS (
    SELECT s.ticker, p.price_date,
           p.close_price
             / LAG(p.close_price) OVER (PARTITION BY p.security_id ORDER BY p.price_date)
             - 1 AS rend
    FROM prices AS p
    JOIN securities AS s ON s.security_id = p.security_id
    WHERE s.ticker IN ('AAPL', 'SPX')
)
SELECT r1.price_date,
       r1.ticker AS titolo,    r1.rend AS rend_titolo,
       r2.ticker AS benchmark, r2.rend AS rend_benchmark,
       (r1.rend - r2.rend) AS rend_attivo
FROM rendimenti AS r1
JOIN rendimenti AS r2 ON r2.price_date = r1.price_date
WHERE r1.ticker = 'AAPL' AND r1.rend IS NOT NULL
  AND r2.ticker = 'SPX'  AND r2.rend IS NOT NULL
ORDER BY r1.price_date;
