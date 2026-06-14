-- ============================================================
-- 01 - Prezzi dei titoli Tech a una data
-- Concetto: JOIN + filtro multiplo (WHERE ... AND) + ORDER BY
-- ------------------------------------------------------------
-- Mostra ticker, settore e prezzo di chiusura di tutti i titoli
-- del settore Tech alla data 2026-05-29, dal piu caro al piu economico.
-- Unisce l'anagrafica (securities) ai prezzi tramite security_id.
-- ============================================================

SELECT s.ticker, s.sector, p.close_price
FROM securities AS s
JOIN prices AS p ON p.security_id = s.security_id
WHERE p.price_date = '2026-05-29'
  AND s.sector = 'Tech'
ORDER BY p.close_price DESC;
