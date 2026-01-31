# Streamlit UI Architecture & Logic Explanation

## Overview
The frontend is built using Streamlit, a Python framework for rapid data app development. The UI is organized into a main app with four navigable pages, each handling specific user workflows.

---

## Architecture

### Directory Structure
```
frontend/streamlit_app/
├── app.py                      # Main landing page
├── config.py                   # Configuration & API endpoints
├── api.py                      # API client wrapper
├── components/
│   ├── charts.py              # Plotly chart utilities
│   └── metrics.py             # Metric display components
└── pages/
    ├── 1_Funds_Explorer.py    # Browse funds
    ├── 2_Fund_Analytics.py    # Detailed fund analysis
    ├── 3_Compare_Funds.py     # Side-by-side comparison
    └── 4_Recommendations.py   # AI-based recommendations
```

### Page Structure
Streamlit automatically discovers pages in the `pages/` directory and creates a sidebar navigation menu. Pages are displayed as `page_number_PageName.py`.

---

## State Management

### Session State
Streamlit uses `st.session_state` to persist variables across reruns (which happen on every user interaction).

```python
# Initialize session state
if "metrics_job_id" not in st.session_state:
    st.session_state.metrics_job_id = None
```

**Why?** Every button click, input change, or selectbox selection triggers a full page rerun. Session state preserves data across these reruns.

### Common Session Variables
- `metrics_job_id` - Tracks async metrics computation job (Fund Analytics page)
- User selections (fund, risk profile, etc.) - Persist across renders

---

## Page Breakdown

### 1️⃣ **app.py** - Landing Page

**Purpose:** Welcome screen & navigation guide

**Components:**
- App title and tagline
- Brief description
- Sidebar navigation instructions

**Key Features:**
- Zero state
- Links to all pages
- Educational messaging

```python
st.title(APP_TITLE)
st.caption("Real NAVs • Risk-adjusted metrics • Explainable recommendations")
st.markdown("👈 Use the sidebar to navigate...")
```

---

### 2️⃣ **1_Funds_Explorer.py** - Fund Catalog Browser

**Purpose:** Browse and filter all available mutual funds

**Workflow:**
1. Fetch all funds from API
2. Display in searchable data table
3. Show fund count metric

**Key Features:**
- Sortable columns
- Search/filter by fund name
- Fund metadata display:
  - Fund House
  - Category & Sub-category
  - Benchmark
  - AUM, TER, Exit Load
  - Launch Date

**Logic:**
```python
funds = get_funds()  # API call
df = pd.DataFrame(funds)
st.dataframe(df[...], width="stretch")  # Interactive table
```

**Why This Structure?**
- Lightweight page for quick browsing
- No heavy computation
- Helps users discover funds before detailed analysis

---

### 3️⃣ **2_Fund_Analytics.py** - Detailed Fund Analysis (Most Complex)

**Purpose:** In-depth metrics, NAV visualization, and metrics computation

**Workflow:**
1. Fund selection via dropdown
2. Display fund details
3. Optional: Sync latest data
4. Visualize NAV history
5. Optional: Compute/recompute metrics
6. Display metrics dashboard

#### Subcomponents:

**Fund Selection:**
```python
fund_map = {f["fund_name"]: f["id"] for f in funds}
fund_name = st.selectbox("Select Fund", fund_map.keys())
fund_id = fund_map[fund_name]
```

**Fund Details Section:**
- Grid of metrics (4 columns × 2 rows)
- TER, AUM, Exit Load, Stamp Duty
- Category, Launch Date

**Data Sync Section:**
- 🔄 Sync button triggers background job
- Shows sync progress
- Handles errors gracefully

```python
if st.button("🔄 Sync Data"):
    with st.spinner("Syncing..."):
        result = sync_fund(fund_id)
        if result.get('success'):
            st.success("✅ Sync completed!")
        else:
            st.error("❌ Sync failed!")
```

**NAV Chart:**
- Converts NAV data to DataFrame
- Uses Plotly for interactive line chart
- X-axis: nav_date, Y-axis: nav_value

```python
nav = get_nav(fund_id)
nav_df = pd.DataFrame(nav)
nav_df["nav_date"] = pd.to_datetime(nav_df["nav_date"])
st.plotly_chart(px.line(nav_df, x="nav_date", y="nav_value", ...))
```

**Metrics Computation:**

*Key Challenge:* Metrics computation is slow (~1-5 minutes). Streamlit requires async patterns.

*Solution:* Job-based architecture with polling:

1. **Start Job:**
```python
if st.button("⚙️ Compute Metrics"):
    job = start_metrics_job(fund_id)
    st.session_state.metrics_job_id = job["job_id"]
    st.info("Computing...")
    st.rerun()  # Force rerun to show polling UI
```

2. **Poll for Completion:**
```python
job_id = st.session_state.metrics_job_id
if job_id:
    with st.spinner("Computing..."):
        progress_bar = st.progress(0)
        for i in range(300):  # Max 300 polls (2.5 min)
            job = get_metrics_job(job_id)
            progress_bar.progress(job["progress"])
            
            if job["status"] == "SUCCESS":
                st.success("✅ Metrics computed!")
                st.session_state.metrics_job_id = None
                st.rerun()  # Refresh to show new metrics
                break
            
            time.sleep(0.5)
```

**Why This Pattern?**
- Streamlit is synchronous; we need async-like behavior
- Polling simulates waiting without blocking
- Session state tracks job across reruns
- Progress bar gives user feedback

**Metrics Display:**
- Table of metrics with values & status
- Health score visual indicator
- Detailed explanations for each metric

```python
metrics_data = {
    "Metric": ["Std Deviation", "Sharpe Ratio", "Sortino Ratio", ...],
    "Value": [metrics["std_deviation"], metrics["sharpe_ratio"], ...],
    "Status": ["✅", "✅", "⚠️", ...]
}
st.dataframe(pd.DataFrame(metrics_data))
```

#### Stale Data Detection:
```python
if metrics_current:
    last_updated = datetime.fromisoformat(metrics_current["as_of_date"]).date()
    if last_updated < date.today():
        st.warning("⏳ Metrics are stale. Click 'Recompute' for latest data.")
```

---

### 4️⃣ **3_Compare_Funds.py** - Side-by-Side Comparison

**Purpose:** Compare metrics across multiple selected funds

**Workflow:**
1. Multi-select funds
2. Fetch metrics for each
3. Display side-by-side table
4. Add comparative analysis

**Key Features:**
- Multi-select widget for fund selection
- Metrics comparison table
- Visual diff highlights
- Ranking by specific metric

```python
selected_funds = st.multiselect("Select Funds", fund_map.keys())
fund_ids = [fund_map[name] for name in selected_funds]

comparison_data = []
for fund_id in fund_ids:
    metrics = get_metrics(fund_id)
    comparison_data.append(metrics)

st.dataframe(pd.DataFrame(comparison_data))
```

---

### 5️⃣ **4_Recommendations.py** - AI-Based Recommendations

**Purpose:** Get personalized fund recommendations based on risk profile

**Workflow:**
1. User selects risk profile (low/medium/high)
2. User selects investment category
3. User selects top-N funds to show
4. API computes weighted scores
5. Display ranked recommendations with explanations

**Key Features:**
- Risk profile selector (radio buttons)
- Category selector
- Top-N slider (3-10 funds)
- Score-based ranking
- Detailed metric breakdown per fund
- AI-generated explanation

**Logic:**
```python
if st.button("Get Recommendations"):
    payload = {
        "risk_profile": risk,
        "investment_horizon_years": 5,
        "category": category,
        "top_n": top_n,
    }
    result = recommend(payload)  # API call
    
    if result.get("recommendations"):
        df = pd.DataFrame(result["recommendations"])
        st.dataframe(df[["fund_name", "score"]])
        
        for idx, row in df.iterrows():
            with st.expander(f"📊 {row['fund_name']} - Score: {row['score']:.2f}"):
                metrics = row.get("key_metrics", {})
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Alpha", f"{metrics.get('alpha', 'N/A'):.4f}")
                with col2:
                    st.metric("Sharpe", f"{metrics.get('sharpe', 'N/A'):.2f}")
                # ... more metrics
                st.info(f"**Why?** {row['explanation']}")
```

**Why Expanders?**
- Each fund is a collapsible section
- Keeps page clean while showing detailed data
- Users can drill down as needed

---

## API Client (`api.py`)

Acts as a wrapper around FastAPI backend calls.

```python
def get_funds():
    """Fetch all mutual funds"""
    response = requests.get(f"{API_BASE}/funds")
    return response.json()

def start_metrics_job(fund_id: int):
    """Trigger metrics computation job"""
    response = requests.post(f"{API_BASE}/metrics/jobs/{fund_id}")
    return response.json()

def get_metrics_job(job_id: int):
    """Poll job status"""
    response = requests.get(f"{API_BASE}/metrics/jobs/{job_id}")
    return response.json()

def recommend(payload: dict):
    """Get fund recommendations"""
    response = requests.post(f"{API_BASE}/recommend", json=payload)
    return response.json()
```

**Error Handling:**
```python
try:
    result = get_metrics(fund_id)
except Exception as e:
    st.error(f"Error: {str(e)}")
    st.info("Ensure the backend API is running.")
```

---

## UI Components (`components/`)

### metrics.py
Helper functions for displaying metric values safely.

```python
def safe_metric(label: str, value, format_str: str = ".2f"):
    """Safely display a metric, handling None/NaN values"""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        st.metric(label, "N/A")
    else:
        st.metric(label, f"{float(value):{format_str}}")

def fund_health_score(metrics: dict) -> float:
    """Compute visual health score (0-100) based on metrics"""
    score = 0
    if metrics.get("sharpe_ratio", 0) > 1:
        score += 25
    if metrics.get("alpha", 0) > 0:
        score += 25
    # ... more logic
    return min(score, 100)
```

### charts.py
Plotly chart utilities.

```python
def rolling_returns_chart(nav_data: pd.DataFrame):
    """Generate rolling returns chart"""
    nav_data["rolling_1y"] = nav_data["nav_value"].pct_change(252)
    return px.line(nav_data, y="rolling_1y", title="Rolling 1Y Returns")
```

---

## Critical UI Patterns

### 1. **Spinner + Status Text**
```python
with st.spinner("Loading..."):
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i in range(100):
        progress_bar.progress(i)
        status_text.text(f"Progress: {i}%")
        time.sleep(0.1)
```

### 2. **Expander for Details**
```python
with st.expander("📊 Advanced Metrics"):
    st.dataframe(advanced_data)
    st.write("Detailed explanations...")
```

### 3. **Columns for Layout**
```python
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Metric A", value_a)
with col2:
    st.metric("Metric B", value_b)
with col3:
    st.metric("Metric C", value_c)
```

### 4. **Conditional Rendering**
```python
if metrics_stale:
    st.warning("⏳ Metrics are stale")
else:
    st.success("✅ Metrics current")
```

---

## Error Handling Philosophy

**User-Friendly Errors:**
```python
try:
    result = api_call()
except Exception as e:
    st.error("❌ Something went wrong!")
    with st.expander("📋 Technical Details"):
        st.code(str(e))
```

**Never Show Traceback** - Instead, show actionable messages:
- ✅ "Fund not found. Try selecting a different fund."
- ✅ "API is unavailable. Ensure backend is running."
- ✅ "Insufficient NAV data. Check fund history."

---

## Performance Considerations

### Caching
```python
@st.cache_data
def get_funds():
    """Cache fund list for 1 hour"""
    return api.get_funds()
```

### Lazy Loading
Only compute metrics when explicitly requested (not on page load).

### Session State for Polling
Avoids repeatedly fetching completed jobs.

---

## Future Enhancements

1. **Dark Mode** - Add theme toggle
2. **Export Metrics** - CSV/PDF downloads
3. **Watchlist** - Save favorite funds
4. **Alerts** - Notify when metrics change
5. **Portfolio Optimizer** - Optimize fund allocation
6. **Mobile Responsiveness** - Better mobile layout