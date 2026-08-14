import streamlit as st


st.set_page_config(
    page_title="LH Nautical | Data & Analytics",
    page_icon="⚓",
    layout="wide",
)

pages = {
    "Dashboard": [
        st.Page(
            "pages/overview.py",
            title="Visão Executiva",
            icon=":material/dashboard:",
            default=True,
        ),
        st.Page(
            "pages/customers.py",
            title="Clientes",
            icon=":material/groups:",
        ),
        st.Page(
            "pages/models.py",
            title="Modelos & IA",
            icon=":material/model_training:",
        ),
    ]
}

navigation = st.navigation(pages)
navigation.run()