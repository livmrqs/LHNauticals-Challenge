import plotly.express as px
import streamlit as st

from utils.data_loader import (
    load_elite_category_sales,
    load_elite_customers,
)


# ---------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------

elite_customers = load_elite_customers()
category_sales = load_elite_category_sales()


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def format_brl(value: float) -> str:
    """Format a numeric value as Brazilian Real."""
    formatted = f"{value:,.2f}"

    return (
        "R$ "
        + formatted
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def format_integer(value: int) -> str:
    """Format an integer using Brazilian thousands separator."""
    return f"{value:,}".replace(",", ".")


# ---------------------------------------------------------------------
# KPI calculations
# ---------------------------------------------------------------------

top_customer = elite_customers.loc[
    elite_customers["ticket_medio"].idxmax()
]

average_elite_ticket = elite_customers["ticket_medio"].mean()

top_category = category_sales.loc[
    category_sales["quantidade_total"].idxmax()
]

total_elite_revenue = elite_customers["faturamento_total"].sum()


# ---------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------

st.title("Análise de Clientes")

st.caption(
    "Comportamento dos clientes com alto ticket médio "
    "e elevada diversidade de categorias."
)

st.markdown(
    """
    O segmento abaixo considera exclusivamente os **10 clientes com maior
    ticket médio entre aqueles que compraram produtos de pelo menos
    13 categorias distintas**.
    """
)


# ---------------------------------------------------------------------
# KPIs
# ---------------------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Cliente líder",
        value=f"Cliente {int(top_customer['customer_id'])}",
    )

with col2:
    st.metric(
        label="Maior ticket médio",
        value=format_brl(top_customer["ticket_medio"]),
    )

with col3:
    st.metric(
        label="Categoria mais consumida",
        value=top_category["categoria"],
    )

with col4:
    st.metric(
        label="Unidades da categoria líder",
        value=format_integer(
            int(top_category["quantidade_total"])
        ),
    )


st.divider()


# ---------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------

left_column, right_column = st.columns(
    [1, 1],
    gap="large",
)


# ---------------------------------------------------------------------
# Loyal customer ranking
# ---------------------------------------------------------------------

with left_column:
    st.subheader("Ranking por ticket médio")

    customer_chart_data = (
        elite_customers
        .sort_values(
            "ticket_medio",
            ascending=True,
        )
        .copy()
    )

    customer_chart_data["cliente"] = (
        "Cliente "
        + customer_chart_data["customer_id"].astype(str)
    )

    customer_fig = px.bar(
        customer_chart_data,
        x="ticket_medio",
        y="cliente",
        orientation="h",
        custom_data=[
            "faturamento_total",
            "frequencia",
            "diversidade_categorias",
        ],
        labels={
            "ticket_medio": "",
            "cliente": "",
        },
    )

    customer_fig.update_traces(
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Ticket médio: R$ %{x:,.2f}<br>"
            "Faturamento: R$ %{customdata[0]:,.2f}<br>"
            "Pedidos: %{customdata[1]}<br>"
            "Categorias distintas: %{customdata[2]}"
            "<extra></extra>"
        )
    )

    customer_fig.update_layout(
        showlegend=False,
        height=450,
        margin=dict(
            l=0,
            r=20,
            t=10,
            b=0,
        ),
        xaxis_title=None,
        yaxis_title=None,
    )

    customer_fig.update_xaxes(
        tickprefix="R$ ",
        separatethousands=True,
    )

    st.plotly_chart(
        customer_fig,
        width="stretch",
        config={
            "displayModeBar": False,
        },
    )


# ---------------------------------------------------------------------
# Category ranking
# ---------------------------------------------------------------------

with right_column:
    st.subheader("Categorias mais consumidas")

    category_chart_data = (
        category_sales
        .sort_values(
            "quantidade_total",
            ascending=False,
        )
        .head(10)
        .sort_values(
            "quantidade_total",
            ascending=True,
        )
        .copy()
    )

    category_fig = px.bar(
        category_chart_data,
        x="quantidade_total",
        y="categoria",
        orientation="h",
        labels={
            "quantidade_total": "",
            "categoria": "",
        },
    )

    category_fig.update_traces(
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Unidades compradas: %{x:,.0f}"
            "<extra></extra>"
        )
    )

    category_fig.update_layout(
        showlegend=False,
        height=450,
        margin=dict(
            l=0,
            r=20,
            t=10,
            b=0,
        ),
        xaxis_title=None,
        yaxis_title=None,
    )

    st.plotly_chart(
        category_fig,
        width="stretch",
        config={
            "displayModeBar": False,
        },
    )


# ---------------------------------------------------------------------
# Segment summary
# ---------------------------------------------------------------------

st.divider()

st.subheader("Perfil do segmento")

summary_col1, summary_col2 = st.columns(2)

with summary_col1:
    st.info(
        f"""
        **Clientes de alto valor**

        O cliente **{int(top_customer["customer_id"])}** apresenta o maior
        ticket médio do segmento, atingindo
        **{format_brl(top_customer["ticket_medio"])}**.

        Considerando os dez clientes selecionados, o ticket médio médio
        do grupo é de **{format_brl(average_elite_ticket)}**.
        """
    )

with summary_col2:
    st.info(
        f"""
        **Comportamento de consumo**

        **{top_category["categoria"]}** é a categoria com maior volume
        de itens comprados pelos clientes fiéis, totalizando
        **{format_integer(int(top_category["quantidade_total"]))} unidades**.

        Esse comportamento pode servir como ponto de partida para ações
        de cross-sell e segmentação de clientes com perfil semelhante.
        """
    )


# ---------------------------------------------------------------------
# Customer details
# ---------------------------------------------------------------------

st.divider()

st.subheader("Detalhamento dos clientes fiéis")

customer_table = (
    elite_customers
    .sort_values(
        "ticket_medio",
        ascending=False,
    )
    .copy()
)

customer_table = customer_table.rename(
    columns={
        "customer_id": "Cliente",
        "faturamento_total": "Faturamento total",
        "frequencia": "Pedidos",
        "ticket_medio": "Ticket médio",
        "diversidade_categorias": "Categorias distintas",
    }
)

st.dataframe(
    customer_table,
    width="stretch",
    hide_index=True,
)