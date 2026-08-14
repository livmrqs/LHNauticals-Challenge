WITH customer_sales AS (
    SELECT
        customer_id,
        SUM(total) AS faturamento_total,
        COUNT(id) AS frequencia,
        SUM(total) / NULLIF(COUNT(id), 0) AS ticket_medio
    FROM orders
    GROUP BY customer_id
),

customer_diversity AS (
    SELECT
        o.customer_id,
        COUNT(DISTINCT p.category_id) AS diversidade_categorias
    FROM orders AS o
    INNER JOIN order_items AS oi
        ON oi.order_id = o.id
    INNER JOIN product_variants AS pv
        ON pv.id = oi.product_variant_id
    INNER JOIN products AS p
        ON p.id = pv.product_id
    GROUP BY o.customer_id
)

SELECT
    cs.customer_id,
    ROUND(cs.faturamento_total, 2) AS faturamento_total,
    cs.frequencia,
    ROUND(cs.ticket_medio, 2) AS ticket_medio,
    cd.diversidade_categorias
FROM customer_sales AS cs
INNER JOIN customer_diversity AS cd
    ON cd.customer_id = cs.customer_id
WHERE cd.diversidade_categorias >= 13
ORDER BY
    cs.ticket_medio DESC,
    cs.customer_id ASC
LIMIT 10;