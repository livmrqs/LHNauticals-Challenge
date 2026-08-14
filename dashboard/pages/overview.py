import plotly.express as px
import streamlit as st

from utils.data_loader import (
    load_elite_customers,
    load_orders,
    load_weekday_sales,
)


# ---------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------

orders = load_orders()
elite_customers = load_elite_customers()
weekday_sales = load_weekday_sales()


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

total_orders = orders["id"].nunique()
total_customers = orders["customer_id"].nunique()
average_ticket = orders["total"].mean()

min_date = orders["placed_at"].min()
max_date = orders["placed_at"].max()

analysis_period = (
    f"{min_date.year} — {max_date.year}"
)


# ---------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------

st.title("LH Nautical")
st.caption("Data & Analytics Dashboard")

st.markdown(
    """
    Visão consolidada dos principais resultados obtidos durante
    a análise dos dados operacionais da LH Nautical.
    """
)


# ---------------------------------------------------------------------
# KPIs
# ---------------------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Pedidos",
        value=format_integer(total_orders),
    )

with col2:
    st.metric(
        label="Clientes",
        value=format_integer(total_customers),
    )

with col3:
    st.metric(
        label="Ticket médio",
        value=format_brl(average_ticket),
    )

with col4:
    st.metric(
        label="Período analisado",
        value=analysis_period,
    )


st.divider()


# ---------------------------------------------------------------------
# Main charts
# ---------------------------------------------------------------------

left_column, right_column = st.columns(
    [1, 1],
    gap="large",
)


# ---------------------------------------------------------------------
# Weekday sales
# ---------------------------------------------------------------------

with left_column:
    st.subheader("Vendas médias por dia da semana")

    weekday_chart_data = weekday_sales.sort_values(
        "media_vendas",
        ascending=True,
    ).copy()

    weekday_fig = px.bar(
        weekday_chart_data,
        x="media_vendas",
        y="dia_semana",
        orientation="h",
        labels={
            "media_vendas": "Média de vendas",
            "dia_semana": "",
        },
        custom_data=[
            "dias_no_calendario",
            "dias_sem_venda",
        ],
    )

    weekday_fig.update_traces(
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Média: R$ %{x:,.2f}<br>"
            "Dias analisados: %{customdata[0]}<br>"
            "Dias sem venda: %{customdata[1]}"
            "<extra></extra>"
        )
    )

    weekday_fig.update_layout(
        showlegend=False,
        margin=dict(
            l=0,
            r=20,
            t=10,
            b=0,
        ),
        xaxis_title=None,
        yaxis_title=None,
        height=420,
    )

    weekday_fig.update_xaxes(
        tickprefix="R$ ",
        separatethousands=True,
    )

    st.plotly_chart(
        weekday_fig,
        width="stretch",
        config={
            "displayModeBar": False,
        },
    )


# ---------------------------------------------------------------------
# Loyal customers
# ---------------------------------------------------------------------

with right_column:
    st.subheader("Top 10 clientes fiéis")

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
        labels={
            "ticket_medio": "Ticket médio",
            "cliente": "",
        },
        custom_data=[
            "faturamento_total",
            "frequencia",
            "diversidade_categorias",
        ],
    )

    customer_fig.update_traces(
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Ticket médio: R$ %{x:,.2f}<br>"
            "Faturamento: R$ %{customdata[0]:,.2f}<br>"
            "Pedidos: %{customdata[1]}<br>"
            "Categorias: %{customdata[2]}"
            "<extra></extra>"
        )
    )

    customer_fig.update_layout(
        showlegend=False,
        margin=dict(
            l=0,
            r=20,
            t=10,
            b=0,
        ),
        xaxis_title=None,
        yaxis_title=None,
        height=420,
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
# Executive insights
# ---------------------------------------------------------------------

st.divider()

st.subheader("Principais insights")

worst_weekday = weekday_sales.loc[
    weekday_sales["media_vendas"].idxmin()
]

best_customer = elite_customers.loc[
    elite_customers["ticket_medio"].idxmax()
]

insight_col1, insight_col2 = st.columns(2)

with insight_col1:
    st.info(
        f"""
        **Menor média de vendas físicas**

        {worst_weekday["dia_semana"]} apresentou a menor média diária,
        com **{format_brl(worst_weekday["media_vendas"])}**.

        O cálculo considera também os dias em que a loja esteve aberta
        mas não registrou vendas.
        """
    )

with insight_col2:
    st.info(
        f"""
        **Cliente com maior ticket médio**

        O cliente **{int(best_customer["customer_id"])}** lidera o
        segmento de clientes fiéis, com ticket médio de
        **{format_brl(best_customer["ticket_medio"])}**.

        Esse cliente comprou produtos de
        **{int(best_customer["diversidade_categorias"])} categorias
        distintas**.
        """
    )