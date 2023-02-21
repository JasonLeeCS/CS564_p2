--answer: 8365
SELECT COUNT(*)

FROM
( 
    SELECT *
    FROM category
    GROUP BY itemID
    HAVING COUNT(category) = 4
);