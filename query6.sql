--answer: 6717
SELECT COUNT(*)

FROM 
(
    SELECT *
    FROM item INNER JOIN bid ON item.userID = bid.userID
    GROUP BY item.userID
);