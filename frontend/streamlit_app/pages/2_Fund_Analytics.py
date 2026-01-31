import time
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date

from frontend.streamlit_app.api import (
    get_funds,
    get_nav,
    get_metrics,
    start_metrics_job,
    get_metrics_job,
    sync_fund,
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

# Find the selected fund details
selected_fund = next((f for f in funds if f["id"] == fund_id), {})

# ---------- Fund Details ----------
if selected_fund:
    st.subheader("📋 Fund Details")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Fund House", selected_fund.get("fund_house", "N/A"))
    with col2:
        ter = selected_fund.get("ter", "N/A")
        st.metric("TER (%)", ter if ter and ter != "N/A" else "N/A")
    with col3:
        aum = selected_fund.get("aum", "N/A")
        st.metric("AUM (₹ Cr)", aum if aum and aum != "N/A" else "N/A")
    with col4:
        launch_date = selected_fund.get("launch_date", "N/A")
        st.metric("Launch Date", launch_date if launch_date and launch_date != "N/A" else "N/A")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        exit_load = selected_fund.get("exit_load", "N/A")
        st.metric("Exit Load (%)", exit_load if exit_load and exit_load != "N/A" else "N/A")
    with col2:
        stamp_duty = selected_fund.get("stamp_duty", "N/A")
        st.metric("Stamp Duty (%)", stamp_duty if stamp_duty and stamp_duty != "N/A" else "N/A")
    with col3:
        category = selected_fund.get("category", "N/A")
        st.metric("Category", category if category and category != "N/A" else "N/A")
    
    st.markdown("---")
    
    # ---------- Data Sync ----------
    st.subheader("🔄 Data Sync")
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.caption("Sync latest fund data from external APIs")
    
    with col2:
        if st.button("🔄 Sync Data", key=f"sync_button_{fund_id}"):
            with st.spinner("Syncing fund data..."):
                progress_bar = st.progress(0)
                status_placeholder = st.empty()
                
                try:
                    result = sync_fund(fund_id)
                    
                    if result.get('success'):
                        progress_bar.progress(100)
                        st.success("✅ Sync completed successfully!")
                        
                        # Show sync results
                        with st.expander("📊 Sync Details"):
                            if result.get('messages'):
                                st.info("\n".join(result['messages']))
                            st.metric("Details Updated", "Yes" if result.get('details_updated') else "No")
                            st.metric("NAV Records Added", result.get('nav_records_added', 0))
                            st.metric("Metrics Recomputed", "Yes" if result.get('metrics_computed') else "No")
                        
                        # Refresh the page to show updated data
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ Sync failed!")
                        with st.expander("📋 Error Details"):
                            if result.get('errors'):
                                for error in result['errors']:
                                    st.error(f"• {error}")
                            if result.get('messages'):
                                st.info("\n".join(result['messages']))
                
                except Exception as e:
                    st.error(f"❌ Sync error: {str(e)}")
    
    with col3:
        st.caption("")  # Alignment
    
    st.markdown("---")

# ---------- NAV ----------
nav = get_nav(fund_id)
nav_df = pd.DataFrame(nav)
nav_df["nav_date"] = pd.to_datetime(nav_df["nav_date"])

st.plotly_chart(
    px.line(nav_df, x="nav_date", y="nav_value", title="NAV Over Time"),
    width="stretch",
)

# ---------- Compute Metrics ----------
col1, col2 = st.columns([3, 1])

# Check if metrics exist and when they were last updated
metrics_current = get_metrics(fund_id)
recompute_allowed = False
last_updated_text = ""

if metrics_current:
    last_updated = datetime.fromisoformat(metrics_current["as_of_date"]).date()
    today = date.today()
    
    if last_updated < today:
        recompute_allowed = True
        last_updated_text = f"Last Updated: {last_updated} | Stale Data"
    else:
        last_updated_text = f"Last Updated: {last_updated} | Current"
    
    col1.caption(last_updated_text)

with col2:
    button_disabled = metrics_current is not None and not recompute_allowed
    if st.button("⚙️ Recompute" if recompute_allowed else "⚙️ Compute Metrics", 
                 disabled=button_disabled):
        job = start_metrics_job(fund_id)
        st.session_state.metrics_job_id = job["job_id"]
        if job.get("is_duplicate"):
            st.warning("⏳ Metrics computation already running for this fund. Waiting for it to complete…")
        else:
            st.info("Metrics computation started…")
        st.rerun()

# ---------- Job Polling ----------
job_id = st.session_state.metrics_job_id
if job_id:
    with st.spinner("Computing metrics…"):
        progress_bar = st.progress(0)
        status_placeholder = st.empty()
        max_polls = 300  # Max 2.5 minutes (300 * 0.5 sec)
        
        for i in range(max_polls):
            job = get_metrics_job(job_id)
            progress_percent = job.get("progress", (i + 1) * 5)
            progress_bar.progress(min(progress_percent, 99))  # Don't reach 100 until complete
            
            status_text = f"Status: {job['status']}"
            if job["status"] == "RUNNING":
                status_text += " | Processing…"
            status_placeholder.caption(status_text)

            if job["status"] == "SUCCESS":
                progress_bar.progress(100)
                st.success("✅ Metrics computed successfully!")
                st.session_state.metrics_job_id = None
                time.sleep(1)  # Brief pause before clearing
                st.rerun()  # Refresh to display new metrics
                break

            if job["status"] == "FAILED":
                st.error(f"❌ Computation failed: {job.get('error_message', 'Unknown error')}")
                st.session_state.metrics_job_id = None
                st.stop()

            time.sleep(0.5)
        else:
            # Timeout after max polls
            st.warning("Job is taking longer than expected. Please refresh the page.")
            st.session_state.metrics_job_id = None

# ---------- Metrics ----------
metrics = get_metrics(fund_id)
if not metrics:
    st.warning("⏰ Metrics not available yet. Click 'Compute Metrics' to calculate.")
    st.info("Metrics computation includes Sharpe ratio, Sortino ratio, rolling returns, and more.")
else:
    st.subheader("📊 Fund Metrics Dashboard")
    
    # Create metrics table
    metrics_data = {
        "Metric": [
            "Std Deviation",
            "Sharpe Ratio",
            "Sortino Ratio",
            "1-Year Return",
            "3-Year Return",
            "Alpha",
            "Beta",
            "R² (Correlation)",
            "Upside Capture",
            "Downside Capture",
        ],
        "Value": [
            safe_metric(metrics, "std_deviation", decimals=4),
            safe_metric(metrics, "sharpe_ratio", decimals=2),
            safe_metric(metrics, "sortino_ratio", decimals=2),
            safe_metric(metrics, "rolling_return_1y", "%", decimals=2),
            safe_metric(metrics, "rolling_return_3y", "%", decimals=2),
            safe_metric(metrics, "alpha", decimals=4),
            safe_metric(metrics, "beta", decimals=4),
            safe_metric(metrics, "r_squared", decimals=4),
            safe_metric(metrics, "upside_capture", "%", decimals=2),
            safe_metric(metrics, "downside_capture", "%", decimals=2),
        ],
        "Category": [
            "📉 Risk",
            "📊 Risk-Adjusted",
            "📊 Risk-Adjusted",
            "📈 Returns",
            "📈 Returns",
            "🎯 vs Benchmark",
            "🎯 vs Benchmark",
            "🎯 vs Benchmark",
            "🎯 vs Benchmark",
            "🎯 vs Benchmark",
        ],
        "Description": [
            "Fund volatility (annualized)",
            "Risk-adjusted return (excess return / volatility)",
            "Downside-adjusted return (excess return / downside volatility)",
            "Return over last 12 months",
            "Return over last 36 months",
            "Excess return vs benchmark (% per year)",
            "Systematic risk vs benchmark",
            "Percentage of movement explained by benchmark",
            "Fund gain when benchmark gains",
            "Fund loss when benchmark loses",
        ],
    }
    
    metrics_df = pd.DataFrame(metrics_data)
    
    # Display as styled table
    st.dataframe(
        metrics_df,
        width='stretch',
        hide_index=True,
        use_container_width=True,
        column_config={
            "Metric": st.column_config.TextColumn("📋 Metric", width="large"),
            "Value": st.column_config.TextColumn("💹 Value", width="medium"),
            "Category": st.column_config.TextColumn("📂 Category", width="small"),
            "Description": st.column_config.TextColumn("ℹ️ Description", width="large"),
        },
    )
    
    # Fund Health Score
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        label, color = fund_health_score(metrics)
        st.markdown(
            f"### Fund Health Score: <span style='color:{color}; font-weight:bold'>{label}</span>",
            unsafe_allow_html=True,
        )
        st.caption(f"**As of**: {metrics.get('as_of_date', 'N/A')}")
    
    # Key Insights
    st.markdown("---")
    st.subheader("🔍 Key Insights")
    
    insights = []
    
    # Beta insight
    beta = metrics.get("beta")
    if beta is not None:
        if beta < 0.7:
            insights.append("🛡️ **Defensive Strategy**: Low beta suggests lower volatility than benchmark")
        elif beta > 1.1:
            insights.append("⚡ **Aggressive Strategy**: High beta indicates higher volatility than benchmark")
        else:
            insights.append("⚖️ **Core Equity**: Beta close to 1.0, tracks benchmark closely")
    
    # Alpha insight
    alpha = metrics.get("alpha")
    if alpha is not None:
        if alpha > 0.05:
            insights.append("💰 **Strong Outperformer**: Consistently beats benchmark by >5% annually")
        elif alpha > 0.02:
            insights.append("✅ **Outperformer**: Beats benchmark modestly")
        elif alpha < 0:
            insights.append("⚠️ **Underperformer**: Lags benchmark")
    
    # Capture ratio insight
    upside = metrics.get("upside_capture")
    downside = metrics.get("downside_capture")
    if upside and downside:
        if upside > 0.95 and downside < 0.90:
            insights.append("🎯 **Excellent Risk Control**: Captures upside gains while protecting downside")
        elif downside > upside:
            insights.append("🚨 **Downside Risk**: Loses more than it gains vs benchmark")
    
    # Sharpe ratio insight
    sharpe = metrics.get("sharpe_ratio")
    if sharpe is not None:
        if sharpe > 0.8:
            insights.append("⭐ **High Risk-Adjusted Returns**: Excellent Sharpe ratio")
        elif sharpe > 0.5:
            insights.append("👍 **Good Risk-Adjusted Returns**: Decent Sharpe ratio")
    
    if insights:
        for insight in insights:
            st.info(insight)
    else:
        st.info("📊 Metrics are being analyzed. More insights will appear as data becomes available.")
    
    st.markdown("---")
    
    # Rolling Returns Chart
    st.subheader("📈 Rolling Returns Analysis")
    st.plotly_chart(rolling_returns_chart(nav_df), width='stretch')
