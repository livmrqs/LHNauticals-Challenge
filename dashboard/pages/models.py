import streamlit as st

from utils.data_loader import (
    load_demand_forecast,
    load_product_recommendations,
)


st.title("Modelos & IA")

forecast = load_demand_forecast()
recommendations = load_product_recommendations()

st.subheader("Previsão de demanda")

st.dataframe(
    forecast,
    use_container_width=True,
    hide_index=True,
)

st.subheader("Sistema de recomendação")

st.dataframe(
    recommendations,
    use_container_width=True,
    hide_index=True,
)