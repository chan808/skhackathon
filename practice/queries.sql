-- Original practice queries; not official exam questions.
-- Run against a cleaned lots table, not the raw CSV.

SELECT COUNT(*) AS clean_lots,
       SUM(tested_dies) AS tested,
       SUM(good_dies) AS good,
       1.0 * SUM(good_dies) / SUM(tested_dies) AS weighted_yield,
       AVG(1.0 * good_dies / tested_dies) AS unweighted_lot_yield
FROM lots;

SELECT equipment, product,
       COUNT(*) AS lots,
       1.0 * SUM(good_dies) / SUM(tested_dies) AS weighted_yield
FROM lots
GROUP BY equipment, product
ORDER BY equipment, product;

SELECT equipment,
       CASE WHEN timestamp < '2026-09-09' THEN 'before' ELSE 'after' END AS period,
       1.0 * SUM(good_dies) / SUM(tested_dies) AS weighted_yield
FROM lots
GROUP BY equipment, period
ORDER BY equipment, period;
