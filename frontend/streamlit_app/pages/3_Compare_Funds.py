import streamlit as st
import pandas as pd
from frontend.streamlit_app.api import get_funds, compare_funds

st.header("⚖️ Compare Funds")

funds = get_funds()
fund_map = {f["fund_name"]: f["id"] for f in funds}

selected = st.multiselect(
    "Select funds to compare",
    fund_map.keys(),
)

if len(selected) >= 2:
    ids = [fund_map[name] for name in selected]
    result = compare_funds(ids)

    rows = []
    for f in result["funds"]:
        m = f["metrics"]
        rows.append(
            {
                "Fund": f["fund_name"],
                "Sharpe": m["sharpe_ratio"],
                "Sortino": m["sortino_ratio"],
                "Alpha": m["alpha"],
                "Beta": m["beta"],
                "Std Dev": m["std_deviation"],
            }
        )

    df = pd.DataFrame(rows)
    st.dataframe(df, width="stretch")
else:
    st.info("Select at least 2 funds to compare")
