-- ============================================================
-- 03 - Valore di mercato di ogni fondo a una data
-- Concetto: JOIN multiplo con AGGANCIO TEMPORALE + GROUP BY
-- ------------------------------------------------------------
-- Per ogni fondo: somma di (quantita * prezzo di chiusura) delle
-- sue posizioni al 2026-05-01.
-- ATTENZIONE: il join prices<->holdings va agganciato anche sulla
-- DATA (oltre che su security_id). Senza, ogni posizione verrebbe
-- moltiplicata per tutti i giorni di prezzo del titolo (bug classico).
-- ============================================================

SELECT f.fund_name,
       SUM(h.quantity * p.close_price) AS mkt_value
FROM holdings AS h
JOIN funds  AS f ON f.fund_id = h.fund_id
JOIN prices AS p ON p.security_id = h.security_id
                AND p.price_date  = h.holding_date   -- aggancio su titolo E data
WHERE h.holding_date = '2026-05-01'
GROUP BY f.fund_id, f.fund_name
ORDER BY mkt_value DESC;
