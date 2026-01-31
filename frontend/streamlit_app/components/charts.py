import pandas as pd
import plotly.express as px


def rolling_returns_chart(nav_df: pd.DataFrame):
    nav_df = nav_df.sort_values("nav_date")
    nav_df["returns"] = nav_df["nav_value"].pct_change()

    periods = {
        "1Y": 252,
        "3Y": 756,
        "5Y": 1260,
    }

    data = []
    for label, days in periods.items():
        if len(nav_df) >= days:
            rr = (nav_df["returns"][-days:] + 1).prod() - 1
            data.append({"Period": label, "Return (%)": rr * 100})

    rr_df = pd.DataFrame(data)

    fig = px.bar(
        rr_df,
        x="Period",
        y="Return (%)",
        text_auto=".2f",
        title="Rolling Returns",
    )
    return fig
