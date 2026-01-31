import time
import streamlit as st
import pandas as pd
import plotly.express as px

from frontend.streamlit_app.api import (
    get_funds,
    get_nav,
    get_metrics,
    start_metrics_job,
    get_metrics_job,
)
from frontend.streamlit_app.components.metrics import safe_metric, fund_health_score
from frontend.streamlit_app.components.charts import rolling_returns_chart

if "metrics_job_id" not in st.session_state:
    st.session_state.metrics_job_id = None

st.header("📈 Fund Analytics")

# ---------- Fund Selection ----------
funds = get_funds()
fund_map = {f["fund_name"]: f["id"] for f in funds}
fund_name = st.selectbox("Select Fund", fund_map.keys())
fund_id = fund_map[fund_name]

# ---------- NAV ----------
nav = get_nav(fund_id)
nav_df = pd.DataFrame(nav)
nav_df["nav_date"] = pd.to_datetime(nav_df["nav_date"])

st.plotly_chart(
    px.line(nav_df, x="nav_date", y="nav_value", title="NAV Over Time"),
    width="stretch",
)

# ---------- Compute Metrics ----------
if st.button("⚙️ Compute Metrics"):
    job = start_metrics_job(fund_id)
    st.session_state.metrics_job_id = job["job_id"]
    st.info("Metrics computation started…")

# ---------- Job Polling ----------
job_id = st.session_state.metrics_job_id
if job_id:
    with st.spinner("Computing metrics…"):
        progress = st.progress(0)
        for i in range(20):
            job = get_metrics_job(job_id)
            progress.progress(min((i + 1) * 5, 100))

            if job["status"] == "SUCCESS":
                st.success("Metrics computed!")
                st.session_state.metrics_job_id = None
                break

            if job["status"] == "FAILED":
                st.error(job["error_message"])
                st.session_state.metrics_job_id = None
                st.stop()

            time.sleep(0.5)

# ---------- Metrics ----------
metrics = get_metrics(fund_id)
if not metrics:
    st.warning("Metrics not available yet.")
    st.stop()

st.subheader("📊 Key Metrics")
cols = st.columns(4)
cols[0].metric("Sharpe", safe_metric(metrics, "sharpe_ratio"))
cols[1].metric("Sortino", safe_metric(metrics, "sortino_ratio"))
cols[2].metric("Alpha", safe_metric(metrics, "alpha"))
cols[3].metric("Beta", safe_metric(metrics, "beta"))

label, color = fund_health_score(metrics)
st.markdown(
    f"<h3>Fund Health: <span style='color:{color}'>{label}</span></h3>",
    unsafe_allow_html=True,
)

st.subheader("📈 Rolling Returns")
st.plotly_chart(rolling_returns_chart(nav_df), width="stretch")
