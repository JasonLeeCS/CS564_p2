--answer: 1046871451
SELECT itemID

FROM
(
        SELECT itemID, MAX(currently)
        FROM item
);