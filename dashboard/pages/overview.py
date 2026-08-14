import streamlit as st

from utils.data_loader import load_weekday_sales


st.title("Visão Executiva")
st.caption("LH Nautical | Data & Analytics Dashboard")

weekday_sales = load_weekday_sales()

st.subheader("Média de vendas por dia da semana")

st.dataframe(
    weekday_sales,
    use_container_width=True,
    hide_index=True,
)