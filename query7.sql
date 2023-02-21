--answer: 150
SELECT COUNT(*)

FROM 
(
    SELECT *
    FROM bid AS "b", category AS "c"
    WHERE c.itemID = b.itemID AND b.amount > 100.0
    GROUP BY c.category
    HAVING COUNT(*) >= 1
);