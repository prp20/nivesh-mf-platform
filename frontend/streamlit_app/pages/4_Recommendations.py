import streamlit as st
import pandas as pd
from frontend.streamlit_app.api import recommend

st.header("🧠 Fund Recommendations")

risk = st.selectbox("Risk Profile", ["low", "medium", "high"])
category = st.selectbox("Category", ["Equity", "Debt", "Hybrid"])
top_n = st.slider("Top N funds", 3, 10, 5)

if st.button("Get Recommendations"):
    payload = {
        "risk_profile": risk,
        "investment_horizon_years": 5,
        "category": category,
        "top_n": top_n,
    }

    result = recommend(payload)
    df = pd.DataFrame(result["recommendations"])

    st.subheader("Recommended Funds")
    st.dataframe(
        df[["fund_name", "score", "explanation"]],
        width="stretch"
    )

    st.caption(result["disclaimer"])
