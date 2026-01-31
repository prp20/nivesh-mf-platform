import streamlit as st
import pandas as pd
from frontend.streamlit_app.api import get_funds

st.header("📋 Funds Explorer")

funds = get_funds()
df = pd.DataFrame(funds)

st.dataframe(
    df[
        [
            "fund_name",
            "category",
            "sub_category",
            "benchmark",
            "aum",
            "ter",
            "launch_date",
        ]
    ],
    width="stretch"
)

st.metric("Total Funds", len(df))
