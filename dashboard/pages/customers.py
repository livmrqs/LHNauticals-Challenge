import streamlit as st

from utils.data_loader import (
    load_elite_category_sales,
    load_elite_customers,
)


st.title("Análise de Clientes")

elite_customers = load_elite_customers()
category_sales = load_elite_category_sales()

st.subheader("Clientes fiéis")

st.dataframe(
    elite_customers,
    use_container_width=True,
    hide_index=True,
)

st.subheader("Categorias consumidas")

st.dataframe(
    category_sales,
    use_container_width=True,
    hide_index=True,
)