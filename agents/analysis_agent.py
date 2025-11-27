# analysis_agent.py

import pandas as pd
import matplotlib.pyplot as plt
import re
import numpy as np # Import for random simulation

# --- 1. Generic Helper Functions ---
def clean_data(df):
    """Cleans the price, reviews, and rating columns."""
    df['price'] = df['price'].astype(str).str.replace(r'[₹,]', '', regex=True)
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    
    df['reviews'] = df['reviews'].astype(str).str.replace(r',', '', regex=True)
    df['reviews'] = pd.to_numeric(df['reviews'], errors='coerce').fillna(0).astype(int)
    
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    
    # Drop any rows where price is missing, as they are un-analyzable
    df = df.dropna(subset=['price'])
    return df

# --- NEW FUNCTION: Price API Simulation ---
def fetch_price_history_and_volatility(df_clean):
    """
    Agent Sub-function: Simulates fetching historic data from the new Price API.
    
    In a real project, this is where you'd make API calls for each 
    `product_identifier` to get structured price history data.
    """
    print("⏳ [Agent 2: Analyst] Simulating Price API calls for tracking...")
    
    # For a trial service, we only use a sample of products (e.g., first 20)
    # to avoid hitting rate limits immediately.
    df_sample = df_clean.head(20).copy()
    
    # Simulate Historic Data (Replace this logic with actual API calls)
    def simulate_historic_data(current_price):
        # Current price is the average of the last 7 simulated days
        historic_prices = np.random.normal(loc=current_price, scale=current_price*0.1, size=7)
        historic_prices = np.clip(historic_prices, a_min=current_price*0.5, a_max=None) # Keep prices realistic
        
        historic_avg = np.mean(historic_prices)
        # Price volatility: Use standard deviation normalized by the mean price
        volatility = np.std(historic_prices) / historic_avg
        
        # Simulate a price change percentage (e.g., last 24h)
        price_change_24h = (current_price - historic_prices[-2]) / historic_prices[-2]
        
        return historic_avg, volatility, price_change_24h

    historic_data = df_sample['price'].apply(simulate_historic_data).apply(pd.Series)
    historic_data.columns = ['historic_avg_price', 'price_volatility', 'price_change_24h']
    
    df_sample = pd.concat([df_sample.reset_index(drop=True), historic_data], axis=1)

    # Merge simulated tracking data back into the main DataFrame
    df_merged = df_clean.merge(
        df_sample[['product_identifier', 'historic_avg_price', 'price_volatility', 'price_change_24h']],
        on='product_identifier',
        how='left'
    )
    
    print("✅ [Agent 2: Analyst] Price tracking data simulated and merged.")
    return df_merged

# --- 2. Main Agent Function ---
def run_analysis(df_raw):
    """
    Agent 2: Loads raw DataFrame, cleans it, and returns
    a clean DataFrame and a dictionary of generic plots.
    """
    print(f"📈 [Agent 2: Analyst] Initializing...")
    if df_raw.empty:
        print("❌ [Agent 2: Analyst] No data to analyze.")
        return pd.DataFrame(), {}
        
    df_cleaned = clean_data(df_raw.copy())
    print("🧹 [Agent 2: Analyst] Data cleaning complete.")

    if df_cleaned.empty:
        print("❌ [Agent 2: Analyst] No valid data after cleaning.")
        return pd.DataFrame(), {}

    # NEW STEP: Enrich data with Price API info
    df_cleaned = fetch_price_history_and_volatility(df_cleaned)

    # --- 3. Generate Generic Plots ---
    # ... (Plot generation logic remains the same for brevity) ...
    print("📊 [Agent 2: Analyst] Generating visualizations...")
    plots = {}

    # A. Price Distribution Histogram
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(df_cleaned['price'], bins=30, edgecolor='black', alpha=0.7)
    ax.set_title('Overall Price Distribution')
    ax.set_xlabel('Price (₹)'); ax.set_ylabel('Frequency')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    plots['price_histogram'] = fig

    # B. Price vs. Rating Scatter
    df_rated = df_cleaned.dropna(subset=['rating'])
    if not df_rated.empty:
        fig, ax = plt.subplots(figsize=(10, 6))
        # Use review count for the size of the bubble
        ax.scatter(df_rated['rating'], df_rated['price'], alpha=0.6, 
                    s=df_rated['reviews'].clip(upper=1000)/10) # Clip reviews for sane sizes
        ax.set_title('Price vs. Rating (Size by Review Count)')
        ax.set_xlabel('Rating (1-5)'); ax.set_ylabel('Price (₹)')
        ax.grid(True, linestyle='--', alpha=0.5)
        plots['price_vs_rating_scatter'] = fig

    # C. Top Sellers Bar Chart
    if 'seller' in df_cleaned.columns:
        fig, ax = plt.subplots(figsize=(10, 7))
        seller_counts = df_cleaned['seller'].value_counts().nlargest(15).sort_values()
        seller_counts.plot(kind='barh', ax=ax)
        ax.set_title('Top 15 Sellers by Number of Listings')
        ax.set_xlabel('Number of Listings')
        plots['top_sellers_bar'] = fig
    
    print(f"✅ [Agent 2: Analyst] Analysis complete.")
    return df_cleaned, plots