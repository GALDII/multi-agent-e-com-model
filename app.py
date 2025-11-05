import streamlit as st
from agents.scraper_agent import run_scraper
from agents.analysis_agent import run_analysis
from agents.prediction_agent import run_prediction
from agents.comparison_agent import run_comparison
import pandas as pd

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="Multi-Agent Product Analyzer",
    page_icon="🤖",
    layout="wide"
)

# --- 2. Session State Initialization ---
if 'ran_analysis' not in st.session_state:
    st.session_state.ran_analysis = False
    st.session_state.raw_data = pd.DataFrame()
    st.session_state.clean_data = pd.DataFrame()
    st.session_state.plots = {}
    st.session_state.cheapest_df = pd.DataFrame()
    st.session_state.seller_report_df = pd.DataFrame()
    st.session_state.deals_df = pd.DataFrame()
    st.session_state.importance_df = pd.DataFrame()

# --- 3. Sidebar (for Inputs) ---
with st.sidebar:
    st.title("🤖 Multi-Agent Analyzer")
    st.info("This app uses a team of AI agents to scrape, analyze, and model product data from the web.")
    
    api_key = st.text_input("Enter your SerpApi API Key", type="password")
    product_query = st.text_input("Enter Product to Search", "gold chain for men")

    if st.button("🚀 Run Analysis"):
        st.session_state.ran_analysis = False # Reset flag
        if not api_key:
            st.error("Please enter an API key.")
        elif not product_query:
            st.error("Please enter a product query.")
        else:
            # --- Run Agent 1: Scraper ---
            with st.spinner("🕵️ Agent 1: Scraping data..."):
                st.session_state.raw_data = run_scraper(product_query, api_key)
            
            if st.session_state.raw_data.empty:
                st.error("Agent 1 failed: No data was scraped.")
            else:
                st.success("Agent 1: Scraping complete!")

                # --- Run Agent 2: Analyst ---
                with st.spinner("📈 Agent 2: Analyzing and plotting..."):
                    st.session_state.clean_data, st.session_state.plots = \
                        run_analysis(st.session_state.raw_data)
                st.success("Agent 2: Analysis complete!")

                # --- Run Agent 3: Predictor ---
                with st.spinner("🤖 Agent 3: Building prediction model..."):
                    st.session_state.importance_df, st.session_state.deals_df = \
                        run_prediction(st.session_state.clean_data)
                st.success("Agent 3: Prediction complete!")
                
                # --- Run Agent 4: Comparator ---
                with st.spinner("🔄 Agent 4: Comparing prices..."):
                    st.session_state.cheapest_df, st.session_state.seller_report_df = \
                        run_comparison(st.session_state.clean_data)
                st.success("Agent 4: Comparison complete!")
                
                st.session_state.ran_analysis = True
                st.balloons()

# --- 4. Main Page (for Outputs) ---
st.title("Product Analysis Dashboard")

if not st.session_state.ran_analysis:
    st.info("Enter your API key and a product query in the sidebar to start the analysis.")
else:
    # --- Create Tabs for Each Agent's Output ---
    tab_compare, tab_deals, tab_analysis, tab_model, tab_data = st.tabs([
        "💰 Price Reports (Agent 4)",
        "💎 Potential Deals (Agent 3)",
        "📊 Market Analysis (Agent 2)",
        "🧠 Model Insights (Agent 3)",
        "🗃️ Raw Data (Agent 1)"
    ])

    # --- Tab 1: Comparison Reports ---
    with tab_compare:
        st.header("Top 10 Cheapest Listings")
        st.info("Agent 4 found the 10 cheapest listings for your search query.")
        if not st.session_state.cheapest_df.empty:
            st.dataframe(st.session_state.cheapest_df.style.format({'price': '₹{:,.2f}'}), use_container_width=True)
        else:
            st.warning("No cheapest listings found.")

        st.header("Seller Price Report")
        st.info("Agent 4 summarized the prices and number of listings for each seller.")
        if not st.session_state.seller_report_df.empty:
            st.dataframe(st.session_state.seller_report_df.style.format({
                'min_price': '₹{:,.2f}', 'avg_price': '₹{:,.2f}', 'max_price': '₹{:,.2f}'
            }), use_container_width=True)
        else:
            st.warning("Could not generate seller report.")

    # --- Tab 2: Potential Deals ---
    with tab_deals:
        st.header("Potential Deals Based on AI Prediction")
        st.info("Agent 3 built a model to predict a 'fair' price. A high 'price_difference' suggests a good deal (actual price is much lower than predicted).")
        if not st.session_state.deals_df.empty:
            st.dataframe(st.session_state.deals_df.style.format({
                'price': '₹{:,.2f}', 'predicted_price': '₹{:,.2f}', 'price_difference': '₹{:,.2f}'
            }), use_container_width=True)
        else:
            st.warning("Could not generate a deals report.")

    # --- Tab 3: Market Analysis ---
    with tab_analysis:
        st.header("Market Analysis Plots")
        st.info("Agent 2 created these plots to understand the market landscape.")
        
        if st.session_state.plots.get('price_histogram'):
            st.pyplot(st.session_state.plots.get('price_histogram'))
        if st.session_state.plots.get('price_vs_rating_scatter'):
            st.pyplot(st.session_state.plots.get('price_vs_rating_scatter'))
        if st.session_state.plots.get('top_sellers_bar'):
            st.pyplot(st.session_state.plots.get('top_sellers_bar'))

    # --- Tab 4: Model Insights ---
    with tab_model:
        st.header("Key Price Drivers (Feature Importance)")
        st.info("Agent 3's model found these features to be the most important for predicting price.")
        if not st.session_state.importance_df.empty:
            st.dataframe(st.session_state.importance_df, use_container_width=True)
        else:
            st.warning("Could not determine feature importances.")

    # --- Tab 5: Raw Data ---
    with tab_data:
        st.header("Raw Scraped Data")
        st.info("This is the raw, unprocessed data from Agent 1 (the scraper).")
        st.dataframe(st.session_state.raw_data, use_container_width=True)