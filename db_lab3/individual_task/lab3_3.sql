--3. Вывести бренды, продажи которых строго падают (в месяц) за последние полгода.

WITH st(oid, doo, bid, bname) AS (
        SELECT o.order_id AS oid, o.date_of_order AS doo, b.brand_id AS bid, b.name AS bname
        FROM "order" o
        JOIN ordered_clothes oc ON o.order_id = oc.order_id
        JOIN clothes c ON c.clothes_id = oc.clothes_id
        JOIN brand b ON b.brand_id = c.brand_id
),

stFirst(bname, bid, cnt1) AS (
	SELECT bname, bid, count(bid) as cnt1
    FROM st
    WHERE doo <= now() AND doo > (now() - '1 month'::interval)
    GROUP BY bname, bid
),

stSecond(bname, bid, cnt2) AS (
	SELECT bname, bid, count(bid) as cnt2
    FROM st
    WHERE doo <= (now() - '1 month'::interval) AND doo > (now() - '2 month'::interval)
    GROUP BY bname, bid
),

stThird(bname, bid, cnt3) AS (
	SELECT bname, bid, count(bid) as cnt3
    FROM st
    WHERE doo <= (now() - '2 month'::interval) AND doo > (now() - '3 month'::interval)
    GROUP BY bname, bid
),

stFourth(bname, bid, cnt4) AS (
	SELECT bname, bid, count(bid) as cnt4
    FROM st
    WHERE doo <= (now() - '3 month'::interval) AND doo > (now() - '4 month'::interval)
    GROUP BY bname, bid
),

stFifth(bname, bid, cnt5) AS (
	SELECT bname, bid, count(bid) as cnt5
    FROM st
    WHERE doo <= (now() - '4 month'::interval) AND doo > (now() - '5 month'::interval)
    GROUP BY bname, bid
),

stSixth(bname, bid, cnt6) AS (
	SELECT bname, bid, count(bid) as cnt6
    FROM st
    WHERE doo <= (now() - '5 month'::interval) AND doo > (now() - '6 month'::interval)
    GROUP BY bname, bid
)

SELECT brand.brand_id, brand.name,
       cnt6,
       cnt5,
       cnt4,
       cnt3,
	   cnt2,
	   cnt1
FROM brand

JOIN stFirst ON stFirst.bid = brand.brand_id
JOIN stSecond ON stSecond.bid = brand.brand_id
JOIN stThird ON stThird.bid = brand.brand_id
JOIN stFourth ON stFourth.bid = brand.brand_id
JOIN stFifth ON stFifth.bid = brand.brand_id
JOIN stSixth ON stSixth.bid = brand.brand_id

GROUP BY brand.name,
	   cnt1,
       cnt2,
       cnt3,
       cnt4,
	   cnt5,
	   cnt6,
         brand.brand_id

having cnt6 >= cnt5 and cnt5 >= cnt4 and cnt4 >= cnt3 and cnt3 >= cnt2 and cnt2 >= cnt1

ORDER BY brand.name