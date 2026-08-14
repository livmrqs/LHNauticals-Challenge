import plotly.express as px
import streamlit as st

from utils.data_loader import (
    load_demand_forecast,
    load_product_recommendations,
)


# ---------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------

forecast = load_demand_forecast()
recommendations = load_product_recommendations()


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

MONTH_NAMES = {
    1: "Jan",
    2: "Fev",
    3: "Mar",
    4: "Abr",
    5: "Mai",
    6: "Jun",
    7: "Jul",
    8: "Ago",
    9: "Set",
    10: "Out",
    11: "Nov",
    12: "Dez",
}


def format_decimal(value: float) -> str:
    """Format a decimal value using Brazilian notation."""
    return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# ---------------------------------------------------------------------
# KPI calculations
# ---------------------------------------------------------------------

mae = forecast["erro_absoluto"].mean()

forecast_total = forecast["previsao"].sum()
actual_total = forecast["unidades_vendidas"].sum()

largest_error_row = forecast.loc[
    forecast["erro_absoluto"].idxmax()
]

top_recommendation = recommendations.loc[
    recommendations["similaridade"].idxmax()
]


# ---------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------

st.title("Modelos & IA")

st.caption(
    "Previsão de demanda e recomendações baseadas "
    "no comportamento histórico de compra."
)

st.markdown(
    """
    Esta página apresenta duas aplicações analíticas desenvolvidas a partir
    dos dados da LH Nautical: um **baseline de previsão de demanda** e um
    **sistema de recomendação item-item**.
    """
)


# ---------------------------------------------------------------------
# Forecast section
# ---------------------------------------------------------------------

st.subheader("Previsão de demanda")

st.markdown(
    """
    **Produto analisado:** `Bússola de Bordo 702`

    O baseline utiliza a média móvel das vendas dos três meses anteriores
    para estimar a demanda mensal.
    """
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="MAE",
        value=f"{format_decimal(mae)} unidades",
    )

with col2:
    st.metric(
        label="Previsão Q1/2026",
        value=f"{round(forecast_total)} unidades",
    )

with col3:
    st.metric(
        label="Demanda real Q1/2026",
        value=f"{int(actual_total)} unidades",
    )

with col4:
    st.metric(
        label="Maior erro mensal",
        value=f"{format_decimal(largest_error_row['erro_absoluto'])} un.",
    )


# ---------------------------------------------------------------------
# Forecast chart
# ---------------------------------------------------------------------

forecast_chart_data = forecast.copy()

forecast_chart_data["mes_label"] = forecast_chart_data["mes"].apply(
    lambda date: f"{MONTH_NAMES[date.month]}/{date.year}"
)

forecast_long = forecast_chart_data.melt(
    id_vars=["mes", "mes_label"],
    value_vars=[
        "unidades_vendidas",
        "previsao",
    ],
    var_name="serie",
    value_name="unidades",
)

forecast_long["serie"] = forecast_long["serie"].replace(
    {
        "unidades_vendidas": "Real",
        "previsao": "Previsto",
    }
)

forecast_fig = px.bar(
    forecast_long,
    x="mes_label",
    y="unidades",
    color="serie",
    barmode="group",
    labels={
        "mes_label": "",
        "unidades": "Unidades",
        "serie": "",
    },
)

forecast_fig.update_traces(
    hovertemplate=(
        "<b>%{x}</b><br>"
        "%{fullData.name}: %{y:.2f} unidades"
        "<extra></extra>"
    )
)

forecast_fig.update_layout(
    height=430,
    margin=dict(
        l=0,
        r=20,
        t=20,
        b=0,
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
    ),
    xaxis_title=None,
    yaxis_title="Unidades",
)

st.plotly_chart(
    forecast_fig,
    width="stretch",
    config={
        "displayModeBar": False,
    },
)

# ---------------------------------------------------------------------
# Forecast insight
# ---------------------------------------------------------------------

st.info(
    f"""
    **Leitura do modelo**

    O baseline apresentou MAE de **{format_decimal(mae)} unidades**.

    O maior desvio ocorreu em
    **{MONTH_NAMES[largest_error_row["mes"].month]}/{largest_error_row["mes"].year}**,
    quando a demanda real foi de
    **{int(largest_error_row["unidades_vendidas"])} unidades**
    e a previsão foi de
    **{format_decimal(largest_error_row["previsao"])} unidades**.

    O resultado evidencia a dificuldade da média móvel em capturar
    mudanças bruscas ou comportamentos sazonais da demanda.
    """
)


st.divider()


# ---------------------------------------------------------------------
# Recommendation section
# ---------------------------------------------------------------------

st.subheader("Sistema de recomendação")

st.markdown(
    """
    **Produto de referência:** `Motor de Popa 1949`

    As recomendações são baseadas na Similaridade de Cosseno entre
    produtos, utilizando os clientes que compraram cada item.
    """
)


rec_col1, rec_col2 = st.columns(
    [1, 3],
    gap="large",
)


# ---------------------------------------------------------------------
# Recommendation KPI
# ---------------------------------------------------------------------

with rec_col1:
    st.metric(
        label="Principal recomendação",
        value=top_recommendation["produto"],
    )

    st.metric(
        label="Similaridade",
        value=format_decimal(
            top_recommendation["similaridade"]
        ),
    )

    st.caption(
        "A similaridade representa proximidade entre padrões "
        "de compradores, e não probabilidade de compra."
    )


# ---------------------------------------------------------------------
# Recommendation ranking
# ---------------------------------------------------------------------

with rec_col2:
    recommendation_chart_data = (
        recommendations
        .sort_values(
            "similaridade",
            ascending=True,
        )
        .copy()
    )

    recommendation_fig = px.bar(
        recommendation_chart_data,
        x="similaridade",
        y="produto",
        orientation="h",
        labels={
            "similaridade": "Similaridade",
            "produto": "",
        },
        custom_data=[
            "product_id",
        ],
    )

    recommendation_fig.update_traces(
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Product ID: %{customdata[0]}<br>"
            "Similaridade: %{x:.4f}"
            "<extra></extra>"
        )
    )

    recommendation_fig.update_layout(
        showlegend=False,
        height=380,
        margin=dict(
            l=0,
            r=20,
            t=10,
            b=0,
        ),
        xaxis_title="Similaridade de Cosseno",
        yaxis_title=None,
    )

    st.plotly_chart(
        recommendation_fig,
        width="stretch",
        config={
            "displayModeBar": False,
        },
    )


# ---------------------------------------------------------------------
# Recommendation insight
# ---------------------------------------------------------------------

st.info(
    f"""
    **Oportunidade de recomendação**

    O produto **{top_recommendation["produto"]}** apresentou o padrão
    de compradores mais semelhante ao `Motor de Popa 1949`.

    Esse resultado pode ser utilizado como ponto de partida para uma
    vitrine de produtos relacionados, embora testes de conversão sejam
    necessários antes de concluir que a recomendação gera aumento real
    nas vendas.
    """
)


# ---------------------------------------------------------------------
# Model details
# ---------------------------------------------------------------------

st.divider()

st.subheader("Resultados detalhados")

tab_forecast, tab_recommendations = st.tabs(
    [
        "Previsão de demanda",
        "Recomendações",
    ]
)

with tab_forecast:
    forecast_table = forecast.copy()

    forecast_table["mes"] = forecast_table["mes"].apply(
        lambda date: (
            f"{MONTH_NAMES[date.month]}/{date.year}"
        )
    )

    forecast_table = forecast_table.rename(
        columns={
            "mes": "Mês",
            "unidades_vendidas": "Demanda real",
            "previsao": "Previsão",
            "erro_absoluto": "Erro absoluto",
        }
    )

    st.dataframe(
        forecast_table,
        width="stretch",
        hide_index=True,
    )


with tab_recommendations:
    recommendations_table = recommendations.copy()

    recommendations_table = recommendations_table.rename(
        columns={
            "product_id": "Product ID",
            "produto": "Produto",
            "similaridade": "Similaridade",
        }
    )

    st.dataframe(
        recommendations_table[
            [
                "Produto",
                "Similaridade",
                "Product ID",
            ]
        ],
        width="stretch",
        hide_index=True,
    )