import streamlit as st
import pandas as pd
from frontend.streamlit_app.api import recommend

st.header("🧠 Fund Recommendations")

risk = st.selectbox("Risk Profile", ["low", "medium", "high"])
category = st.selectbox("Category", ["Equity", "Debt", "Hybrid"])
top_n = st.slider("Top N funds", 3, 10, 5)

if st.button("Get Recommendations"):
    try:
        payload = {
            "risk_profile": risk,
            "investment_horizon_years": 5,
            "category": category,
            "top_n": top_n,
        }

        result = recommend(payload)
        
        # Check for API errors
        if result.get("error"):
            st.error(f"❌ Error: {result.get('message')}")
            st.info("The recommendation engine encountered an error. Please check that the backend is running correctly.")
        elif result.get("recommendations"):
            df = pd.DataFrame(result["recommendations"])

            st.subheader("Recommended Funds")
            
            # Display key columns
            display_columns = ["fund_name", "score"]
            if "key_metrics" in df.columns:
                st.dataframe(
                    df[display_columns],
                    width="stretch"
                )
                
                # Show detailed metrics for each fund
                for idx, row in df.iterrows():
                    with st.expander(f"📊 {row['fund_name']} - Score: {row['score']:.2f}"):
                        metrics = row.get("key_metrics", {})
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Alpha", f"{metrics.get('alpha', 'N/A'):.4f}" if metrics.get('alpha') else "N/A")
                            st.metric("Beta", f"{metrics.get('beta', 'N/A'):.4f}" if metrics.get('beta') else "N/A")
                        
                        with col2:
                            st.metric("Sharpe Ratio", f"{metrics.get('sharpe', 'N/A'):.2f}" if metrics.get('sharpe') else "N/A")
                            st.metric("Sortino Ratio", f"{metrics.get('sortino', 'N/A'):.2f}" if metrics.get('sortino') else "N/A")
                        
                        with col3:
                            st.metric("Std Dev", f"{metrics.get('std_dev', 'N/A'):.4f}" if metrics.get('std_dev') else "N/A")
                        
                        if row.get("explanation"):
                            st.info(f"**Why this fund?** {row['explanation']}")
            else:
                st.dataframe(df, width="stretch")

            st.caption(result.get("disclaimer", ""))
        else:
            st.warning("No recommendations found for the selected criteria.")
    
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.info("Please check that the backend API is running and try again.")
