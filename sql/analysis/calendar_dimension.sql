WITH date_range AS (
    SELECT
        CAST(MIN(placed_at) AS DATE) AS min_date,
        CAST(MAX(placed_at) AS DATE) AS max_date
    FROM orders
),

dim_calendar AS (
    SELECT
        CAST(calendar_date AS DATE) AS date,
        EXTRACT(ISODOW FROM calendar_date) AS weekday_number,
        CASE EXTRACT(ISODOW FROM calendar_date)
            WHEN 1 THEN 'Segunda-feira'
            WHEN 2 THEN 'Terça-feira'
            WHEN 3 THEN 'Quarta-feira'
            WHEN 4 THEN 'Quinta-feira'
            WHEN 5 THEN 'Sexta-feira'
            WHEN 6 THEN 'Sábado'
            WHEN 7 THEN 'Domingo'
        END AS weekday_name
    FROM date_range,
         GENERATE_SERIES(
             min_date,
             max_date,
             INTERVAL 1 DAY
         ) AS dates(calendar_date)
),

daily_sales AS (
    SELECT
        c.date,
        c.weekday_number,
        c.weekday_name,
        COALESCE(SUM(o.total), 0) AS vendas_diarias
    FROM dim_calendar AS c
    LEFT JOIN orders AS o
        ON CAST(o.placed_at AS DATE) = c.date
        AND o.channel = 'pos'
    GROUP BY
        c.date,
        c.weekday_number,
        c.weekday_name
)

SELECT
    weekday_name AS dia_semana,
    ROUND(AVG(vendas_diarias), 2) AS media_vendas
FROM daily_sales
GROUP BY
    weekday_number,
    weekday_name
ORDER BY media_vendas ASC;