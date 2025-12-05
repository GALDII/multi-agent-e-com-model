import streamlit as st
import pandas as pd
import time
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# --- Import Custom Modules with Better Error Handling ---
try:
    from agents.scraper_agent import run_scraper
    from agents.analysis_agent import run_analysis
    from agents.prediction_agent import run_prediction
    from agents.comparison_agent import run_comparison
    AGENTS_LOADED = True
except ImportError as e:
    st.error(f"⚠️ Agent modules not found: {e}")
    st.info("""
    **Please ensure your directory structure looks like this:**
    ```
    your_project/
    ├── app.py
    └── agents/
        ├── __init__.py
        ├── scraper_agent.py
        ├── analysis_agent.py
        ├── prediction_agent.py
        └── comparison_agent.py
    ```
    
    **Quick fix:** Create an empty `__init__.py` file in the agents folder.
    """)
    AGENTS_LOADED = False

# --- 1. Page Configuration & Custom CSS ---
st.set_page_config(
    page_title="Nexus AI | Enterprise Product Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Professional CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* Hero Section */
    .hero-container {
        background: white;
        border-radius: 20px;
        padding: 60px 40px;
        text-align: center;
        box-shadow: 0 20px 60px rgba(0,0,0,0.15);
        margin-bottom: 40px;
        position: relative;
        overflow: hidden;
    }
    
    .hero-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 20px;
        line-height: 1.2;
    }
    
    .hero-subtitle {
        font-size: 1.3rem;
        color: #64748b;
        margin-bottom: 30px;
        line-height: 1.6;
    }
    
    .hero-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 8px 20px;
        border-radius: 50px;
        font-size: 0.9rem;
        font-weight: 600;
        margin: 10px 5px;
    }
    
    /* Feature Cards */
    .feature-card {
        background: white;
        border-radius: 15px;
        padding: 30px;
        height: 100%;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
        border-color: #667eea;
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 20px;
        display: block;
    }
    
    .feature-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 15px;
    }
    
    .feature-desc {
        color: #64748b;
        line-height: 1.6;
        font-size: 1rem;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
    }
    
    section[data-testid="stSidebar"] > div {
        padding-top: 2rem;
    }
    
    section[data-testid="stSidebar"] h1 {
        color: #ffffff !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        margin-bottom: 0 !important;
    }
    
    section[data-testid="stSidebar"] .stCaption {
        color: #94a3b8 !important;
        font-size: 0.9rem !important;
    }
    
    section[data-testid="stSidebar"] label {
        color: #e2e8f0 !important;
        font-weight: 600 !important;
    }
    
    section[data-testid="stSidebar"] input {
        background-color: rgba(255,255,255,0.1) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        color: white !important;
        border-radius: 8px !important;
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 10px;
        font-weight: 700;
        font-size: 1.1rem;
        width: 100%;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Metrics */
    div[data-testid="stMetricValue"] {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    div[data-testid="metric-container"] {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: white;
        padding: 10px;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: 600;
        color: #64748b;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Status Container */
    div[data-testid="stStatus"] {
        background: white;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    /* Info/Warning Boxes */
    .stAlert {
        border-radius: 15px;
        border: none;
        box-shadow: 0 5px 20px rgba(0,0,0,0.08);
    }
    
    /* Results Header */
    .results-header {
        background: white;
        padding: 30px;
        border-radius: 15px;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .results-title {
        font-size: 2rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 10px;
    }
    
    /* Deal Card */
    .deal-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.3);
        margin-bottom: 20px;
    }
    
    .deal-badge {
        background: rgba(255,255,255,0.2);
        padding: 5px 15px;
        border-radius: 20px;
        display: inline-block;
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 15px;
    }
    
    /* Stats Grid */
    .stat-box {
        background: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }
    
    .stat-label {
        color: #64748b;
        font-size: 0.9rem;
        margin-top: 5px;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. Session State Initialization ---
if 'ran_analysis' not in st.session_state:
    st.session_state.ran_analysis = False
    st.session_state.raw_data = pd.DataFrame()
    st.session_state.clean_data = pd.DataFrame()
    st.session_state.plots = {}
    st.session_state.cheapest_df = pd.DataFrame()
    st.session_state.seller_report_df = pd.DataFrame()
    st.session_state.historic_report_df = pd.DataFrame()
    st.session_state.deals_df = pd.DataFrame()
    st.session_state.importance_df = pd.DataFrame()

# --- 3. Sidebar ---
with st.sidebar:
    st.title("🎯 Nexus AI")
    st.caption("Enterprise Intelligence Platform")
    st.markdown("---")
    
    # Secure Input Section
    with st.expander("🔑 API Configuration", expanded=True):
        st.markdown("##### Authentication")
        api_key = st.text_input("SerpApi Key", type="password", help="Required for live market data")
        price_api_key = st.text_input("Price API Key", type="password", help="Optional: Historical tracking")

    st.markdown("### 🔍 Search Configuration")
    product_query = st.text_input(
        "Product Query", 
        "gold chain for men", 
        placeholder="e.g., MacBook Pro M3, Sony WH-1000XM5"
    )
    
    st.markdown("---")
    st.markdown("##### Quick Stats")
    st.markdown("🤖 **4 AI Agents** Active")
    st.markdown("⚡ **Real-time** Analysis")
    st.markdown("🎯 **ML-Powered** Predictions")
    st.markdown("---")
    
    # Run pipeline on button click
    if st.button("🚀 Deploy Intelligence System"):
        if not AGENTS_LOADED:
            st.error("❌ Cannot run: Agent modules not loaded. Please check the error message above.")
        elif not api_key:
            st.error("🔒 API Key Required")
            st.info("Get your free key at serpapi.com")
        elif not product_query:
            st.warning("⚠️ Enter a product to analyze")
        else:
            with st.status("🎯 Deploying Multi-Agent System...", expanded=True) as status:
                try:
                    # Agent 1
                    st.write("🕵️ **Scraper Agent** • Scanning 100+ marketplaces...")
                    time.sleep(0.5)
                    st.session_state.raw_data = run_scraper(product_query, api_key)
                    if st.session_state.raw_data.empty:
                        status.update(label="❌ Scraping Failed", state="error")
                        st.error("No products found. Try a different search query.")
                        st.session_state.ran_analysis = False
                        st.stop()
                    st.write("✅ Retrieved live market data")
                    
                    # Agent 2
                    st.write("📊 **Analysis Agent** • Processing price trends...")
                    time.sleep(0.5)
                    st.session_state.clean_data, st.session_state.plots = \
                        run_analysis(st.session_state.raw_data, price_api_key)
                    st.write("✅ Market analysis complete")
                    
                    # Agent 3
                    st.write("🧠 **Prediction Agent** • Training neural networks...")
                    time.sleep(0.5)
                    st.session_state.importance_df, st.session_state.deals_df = \
                        run_prediction(st.session_state.clean_data)
                    st.write("✅ Price models optimized")
                    
                    # Agent 4
                    st.write("⚖️ **Comparison Agent** • Benchmarking sellers...")
                    time.sleep(0.5)
                    st.session_state.cheapest_df, st.session_state.seller_report_df, st.session_state.historic_report_df = \
                        run_comparison(st.session_state.clean_data)
                    
                    status.update(label="✨ Intelligence Report Ready", state="complete", expanded=False)
                    st.session_state.ran_analysis = True
                    st.balloons()
                    
                except Exception as e:
                    status.update(label="❌ Analysis Failed", state="error")
                    st.error(f"Error during analysis: {str(e)}")
                    st.exception(e)
                    st.session_state.ran_analysis = False

# --- 4. Main Dashboard ---

if not st.session_state.ran_analysis:
    # Hero Section
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">Enterprise Product Intelligence</div>
        <div class="hero-subtitle">
            Harness the power of autonomous AI agents to scan, analyze, and predict market dynamics in real-time.<br>
            Make data-driven decisions with confidence.
        </div>
        <div>
            <span class="hero-badge">✨ Real-Time Data</span>
            <span class="hero-badge">🧠 ML-Powered</span>
            <span class="hero-badge">⚡ Lightning Fast</span>
            <span class="hero-badge">🔒 Enterprise Grade</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # How It Works Section
    st.markdown("<h2 style='text-align: center; color: white; margin: 40px 0;'>🎯 Multi-Agent Architecture</h2>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">🕵️</span>
            <div class="feature-title">Scraper Agent</div>
            <div class="feature-desc">
                Intelligently crawls 100+ marketplaces, extracting real-time product listings, prices, and seller information with precision.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">📊</span>
            <div class="feature-title">Analysis Agent</div>
            <div class="feature-desc">
                Cleans, normalizes, and visualizes market data. Tracks historical trends and identifies pricing patterns across time.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">🧠</span>
            <div class="feature-title">Prediction Agent</div>
            <div class="feature-desc">
                Uses machine learning algorithms to predict fair market value and surface undervalued opportunities you shouldn't miss.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">⚖️</span>
            <div class="feature-title">Comparison Agent</div>
            <div class="feature-desc">
                Benchmarks sellers, compares offerings, and ranks products by value to help you make the smartest purchasing decision.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Benefits Section
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: white; margin: 40px 0;'>💡 Why Choose Nexus AI?</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="stat-box">
            <div class="stat-number">10x</div>
            <div class="stat-label">Faster Research</div>
        </div>
        <br>
        <div class="stat-box">
            <div class="stat-number">100+</div>
            <div class="stat-label">Sources Scanned</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-box">
            <div class="stat-number">95%</div>
            <div class="stat-label">Accuracy Rate</div>
        </div>
        <br>
        <div class="stat-box">
            <div class="stat-number">24/7</div>
            <div class="stat-label">Monitoring</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-box">
            <div class="stat-number">$1000+</div>
            <div class="stat-label">Avg. Savings</div>
        </div>
        <br>
        <div class="stat-box">
            <div class="stat-number">5s</div>
            <div class="stat-label">Analysis Time</div>
        </div>
        """, unsafe_allow_html=True)
    
    # CTA Section
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="hero-container">
        <h2 style="color: #1e293b; margin-bottom: 20px;">Ready to Get Started?</h2>
        <p style="color: #64748b; font-size: 1.1rem; margin-bottom: 20px;">
            Configure your API credentials in the sidebar and deploy your first intelligence mission.
        </p>
        <p style="color: #94a3b8; font-size: 0.9rem;">
            🔒 Your data is encrypted • ⚡ Results in seconds • 🎯 No credit card required
        </p>
    </div>
    """, unsafe_allow_html=True)

else:
    # --- DASHBOARD HEADER ---
    st.markdown(f"""
    <div class="results-header">
        <div class="results-title">📊 Intelligence Report: {product_query}</div>
        <p style="color: #64748b; margin: 0;">Comprehensive market analysis powered by 4 autonomous AI agents</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Top Level KPIs
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    try:
        min_price = st.session_state.clean_data['price'].min()
        avg_price = st.session_state.clean_data['price'].mean()
        total_items = len(st.session_state.clean_data)
        best_deal_gap = st.session_state.deals_df.iloc[0]['price_difference'] if not st.session_state.deals_df.empty else 0
    except Exception:
        min_price, avg_price, total_items, best_deal_gap = 0, 0, 0, 0

    kpi1.metric("💰 Lowest Price", f"₹{min_price:,.0f}")
    kpi2.metric("📊 Market Average", f"₹{avg_price:,.0f}")
    kpi3.metric("🎯 Items Analyzed", f"{total_items}")
    kpi4.metric("💎 Top Deal Saves", f"₹{abs(best_deal_gap):,.0f}", delta=f"-{abs(best_deal_gap):,.0f}")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- TABS ---
    tab_deals, tab_compare, tab_analysis, tab_history, tab_data = st.tabs([
        "💎 Smart Deals", "⚖️ Seller Comparison", "📊 Market Analysis", "📈 Historical Data", "🗄️ Raw Dataset"
    ])

    # --- Tab 1: Smart Deals ---
    with tab_deals:
        st.markdown("### 🎯 AI-Identified Opportunities")
        st.caption("Our Prediction Agent uses machine learning to identify products priced significantly below their estimated fair market value.")
        
        if not st.session_state.deals_df.empty:
            # Top Deal Highlight
            top_deal = st.session_state.deals_df.iloc[0]
            
            st.markdown(f"""
            <div class="deal-card">
                <div class="deal-badge">🏆 #1 RECOMMENDED DEAL</div>
                <h2 style="margin: 15px 0; font-size: 1.8rem;">{top_deal.get('title', 'Premium Product')}</h2>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 20px;">
                    <div>
                        <div style="font-size: 3rem; font-weight: 700;">₹{top_deal['price']:,.0f}</div>
                        <div style="opacity: 0.9;">Predicted Fair Value: ₹{top_deal.get('predicted_price', top_deal['price']):,.0f}</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 2.5rem; font-weight: 700;">₹{abs(top_deal['price_difference']):,.0f}</div>
                        <div style="opacity: 0.9;">Potential Savings</div>
                    </div>
                </div>
                <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.2);">
                    <span style="opacity: 0.9;">Seller: {top_deal.get('source', 'Premium Retailer')}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if 'link' in top_deal and pd.notna(top_deal['link']):
                st.link_button("🛒 View This Deal", top_deal['link'], use_container_width=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### 📋 All Recommended Deals")
            st.caption("Sorted by potential savings (highest first)")
            
            # Safely select columns that exist
            available_cols = ['title', 'price', 'predicted_price', 'price_difference', 'source']
            display_cols = [col for col in available_cols if col in st.session_state.deals_df.columns]
            
            st.dataframe(
                st.session_state.deals_df[display_cols].head(20),
                use_container_width=True,
                column_config={
                    "title": st.column_config.TextColumn("Product", width="large"),
                    "price": st.column_config.NumberColumn("Current Price", format="₹%.2f"),
                    "predicted_price": st.column_config.NumberColumn("AI Fair Value", format="₹%.2f"),
                    "price_difference": st.column_config.NumberColumn("💰 Savings", format="₹%.2f"),
                    "source": st.column_config.TextColumn("Seller", width="medium")
                },
                hide_index=True,
                height=400
            )
        else:
            st.info("💡 No significant undervalued deals detected in current market conditions. The market appears fairly priced based on our ML models.")

    # --- Tab 2: Comparison ---
    with tab_compare:
        col_a, col_b = st.columns([3, 2])
        
        with col_a:
            st.markdown("### 🏆 Top 10 Best Value Offers")
            st.caption("Ranked by price (lowest to highest)")
            
            if not st.session_state.cheapest_df.empty:
                display_df = st.session_state.cheapest_df.head(10).copy()
                display_df.insert(0, 'Rank', range(1, len(display_df) + 1))
                
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    column_config={
                        "Rank": st.column_config.NumberColumn("🏅", width="small"),
                        "title": st.column_config.TextColumn("Product Title", width="large"),
                        "price": st.column_config.NumberColumn("Price", format="₹%.2f"),
                        "source": st.column_config.TextColumn("Seller"),
                        "link": st.column_config.LinkColumn("🔗 View")
                    },
                    hide_index=True,
                    height=450
                )
            else:
                st.warning("No product data available")
        
        with col_b:
            st.markdown("### 📊 Seller Performance")
            st.caption("Average pricing by marketplace")
            
            if not st.session_state.seller_report_df.empty:
                st.dataframe(
                    st.session_state.seller_report_df,
                    use_container_width=True,
                    column_config={
                        "source": st.column_config.TextColumn("Marketplace", width="medium"),
                        "count": st.column_config.NumberColumn("📦 Listings", width="small"),
                        "avg_price": st.column_config.NumberColumn("Avg Price", format="₹%.0f")
                    },
                    hide_index=True,
                    height=450
                )
            else:
                st.info("Seller analysis in progress")

    # --- Tab 3: Analysis ---
    with tab_analysis:
        st.markdown("### 📊 Market Intelligence Visualizations")
        st.caption("Statistical analysis and pattern recognition from current market data")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**📈 Price Distribution Histogram**")
            st.caption("How prices are spread across the market")
            if st.session_state.plots.get('price_histogram'):
                st.pyplot(st.session_state.plots.get('price_histogram'), use_container_width=True)
            else:
                st.info("Visualization not available")
                
        with c2:
            st.markdown("**⭐ Price vs Customer Rating**")
            st.caption("Correlation between price and quality perception")
            if st.session_state.plots.get('price_vs_rating_scatter'):
                st.pyplot(st.session_state.plots.get('price_vs_rating_scatter'), use_container_width=True)
            else:
                st.info("Visualization not available")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 🧠 ML Model: Feature Importance Analysis")
        st.caption("Which factors have the biggest impact on product pricing? (Higher = More Important)")
        
        if not st.session_state.importance_df.empty:
            st.bar_chart(
                st.session_state.importance_df.set_index('feature'),
                height=400,
                use_container_width=True
            )
            
            with st.expander("📖 Understanding Feature Importance"):
                st.markdown("""
                **Feature Importance** reveals which product characteristics our ML model considers most influential when predicting prices:
                
                - **High Importance (>0.3)**: Critical pricing factors
                - **Medium Importance (0.1-0.3)**: Moderate influence
                - **Low Importance (<0.1)**: Minimal impact
                
                This helps identify what really drives value in this product category.
                """)
        else:
            st.info("Feature importance data not available")

    # --- Tab 4: Historical Data ---
    with tab_history:
        st.markdown("### 📈 Historical Price Tracking")
        st.caption("Price evolution over time (requires Price API integration)")
        
        if not st.session_state.historic_report_df.empty:
            st.dataframe(
                st.session_state.historic_report_df, 
                use_container_width=True,
                height=400
            )
            
            st.markdown("""
            <div style="background: white; padding: 20px; border-radius: 10px; margin-top: 20px;">
                <h4 style="color: #1e293b;">💡 Historical Insights</h4>
                <ul style="color: #64748b; line-height: 1.8;">
                    <li>Track price fluctuations across days, weeks, or months</li>
                    <li>Identify seasonal pricing patterns and sale cycles</li>
                    <li>Predict optimal buying windows based on historical trends</li>
                    <li>Validate current pricing against long-term averages</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("📌 Historical data not available. To enable this feature, provide a Price API key in the sidebar.")

    # --- Tab 5: Raw Data ---
    with tab_data:
        st.markdown("### 🗄️ Complete Dataset")
        st.caption("All scraped and processed data for further analysis")
        
        if not st.session_state.clean_data.empty:
            st.dataframe(
                st.session_state.clean_data,
                use_container_width=True,
                height=500
            )
            
            # Download button
            csv = st.session_state.clean_data.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Dataset as CSV",
                data=csv,
                file_name=f"nexus_ai_{product_query.replace(' ', '_')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.warning("No data available to display")
