-- ============================================================
-- 04 - Top holding di ogni fondo + peso sul portafoglio
-- Concetto: argmax (subquery correlata) + rapporto contro un
--           aggregato (derived table per il totale del fondo)
-- ------------------------------------------------------------
-- Per ogni fondo, la posizione piu grande per valore di mercato
-- al 2026-05-01, con il suo peso % sul valore totale del fondo.
-- Tre ingredienti:
--   1) valore di posizione = quantity * close_price (con aggancio data)
--   2) derived table 'sub' = valore totale per fondo (denominatore)
--   3) subquery correlata = filtra la posizione MASSIMA del fondo (argmax)
-- ============================================================

SELECT f.fund_name, s.ticker, s.sector,
       h.quantity * p.close_price AS pos_value,
       h.quantity * p.close_price / sub.val_tot * 100 AS weight_pct
FROM funds AS f
JOIN holdings   AS h ON h.fund_id     = f.fund_id
JOIN prices     AS p ON p.security_id = h.security_id
                    AND p.price_date  = h.holding_date
JOIN securities AS s ON s.security_id = h.security_id
JOIN (   -- valore totale per fondo (denominatore del peso)
        SELECT h3.fund_id,
               SUM(h3.quantity * p3.close_price) AS val_tot
        FROM holdings AS h3
        JOIN prices AS p3 ON p3.security_id = h3.security_id
                         AND p3.price_date  = h3.holding_date
        WHERE h3.holding_date = '2026-05-01'
        GROUP BY h3.fund_id
) AS sub ON sub.fund_id = h.fund_id
WHERE h.holding_date = '2026-05-01'
  AND h.quantity * p.close_price = (   -- argmax: la posizione massima del fondo
        SELECT MAX(h2.quantity * p2.close_price)
        FROM holdings AS h2
        JOIN prices AS p2 ON p2.security_id = h2.security_id
                         AND p2.price_date  = h2.holding_date
        WHERE h2.holding_date = '2026-05-01'
          AND h2.fund_id = h.fund_id
  )
ORDER BY pos_value DESC;
