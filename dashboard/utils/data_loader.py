from pathlib import Path

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "data" / "outputs"


@st.cache_data
def load_elite_customers() -> pd.DataFrame:
    """Load the loyal customers analytical dataset."""
    return pd.read_csv(OUTPUT_DIR / "elite_customers.csv")


@st.cache_data
def load_elite_category_sales() -> pd.DataFrame:
    """Load category sales for the loyal customer segment."""
    return pd.read_csv(OUTPUT_DIR / "elite_category_sales.csv")


@st.cache_data
def load_weekday_sales() -> pd.DataFrame:
    """Load average physical-store sales by weekday."""
    return pd.read_csv(OUTPUT_DIR / "weekday_sales.csv")


@st.cache_data
def load_demand_forecast() -> pd.DataFrame:
    """Load actual and forecast demand for the evaluated product."""
    df = pd.read_csv(
        OUTPUT_DIR / "demand_forecast.csv",
        parse_dates=["mes"],
    )

    return df


@st.cache_data
def load_product_recommendations() -> pd.DataFrame:
    """Load the item-based recommendation ranking."""
    return pd.read_csv(
        OUTPUT_DIR / "product_recommendations.csv"
    )