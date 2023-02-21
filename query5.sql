--answer: 3130
SELECT COUNT(*)

FROM
(
    SELECT *
    FROM item INNER JOIN User on item.userID = User.userID
    WHERE rating > 1000
    GROUP BY item.userID
);