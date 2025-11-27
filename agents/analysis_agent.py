import pandas as pd
import matplotlib.pyplot as plt
import requests # Needed for API calls
import numpy as np # Needed for simulation if API fails

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

# --- 2. Price API Logic ---
def fetch_price_history_and_volatility(df_clean, price_api_key):
    """
    Agent Sub-function: Fetches historic data.
    If a key is provided, it tries to fetch real data.
    Otherwise (or if fetch fails), it falls back to simulation so the app doesn't crash.
    """
    print("⏳ [Agent 2: Analyst] Processing Price History...")
    
    # We create a copy to avoid SettingWithCopy warnings
    # Limiting to top 5 items to save API credits during development/testing
    df_subset = df_clean.head(5).copy() 
    
    historic_avgs = []
    volatilities = []
    changes_24h = []

    for index, row in df_subset.iterrows():
        # Default values (Simulated)
        current_price = row['price']
        
        # --- SIMULATION LOGIC (Default) ---
        # This runs if you don't have the API code set up yet
        historic_prices = np.random.normal(loc=current_price, scale=current_price*0.05, size=7)
        avg_price = np.mean(historic_prices)
        volatility = np.std(historic_prices) / avg_price
        change = (current_price - historic_prices[-2]) / historic_prices[-2]

        # --- REAL API LOGIC (Enable this when ready) ---
        if price_api_key:
            try:
                # ---------------------------------------------------------
                # PASTE YOUR API CODE HERE
                # Example:
                # url = "https://api.your-price-service.com/history"
                # payload = {'token': price_api_key, 'url': row['link']}
                # response = requests.get(url, params=payload)
                # data = response.json()
                # 
                # avg_price = data['average_price']
                # volatility = data['volatility']
                # change = data['change_percentage']
                # ---------------------------------------------------------
                pass # Remove this 'pass' when you add code above
            except Exception as e:
                print(f"⚠️ [Agent 2] API Error for {row.get('title', 'Unknown')}: {e}")
                # Fallback to simulation values calculated above so app keeps working
        
        historic_avgs.append(avg_price)
        volatilities.append(volatility)
        changes_24h.append(change)

    # Assign new columns to the subset
    df_subset['historic_avg_price'] = historic_avgs
    df_subset['price_volatility'] = volatilities
    df_subset['price_change_24h'] = changes_24h
    
    # Merge the enriched data back into the main dataframe
    # We use 'link' as the key to match rows
    df_merged = df_clean.merge(
        df_subset[['link', 'historic_avg_price', 'price_volatility', 'price_change_24h']],
        on='link',
        how='left'
    )
    
    print("✅ [Agent 2: Analyst] Price tracking data merged.")
    return df_merged

# --- 3. Main Agent Function ---
def run_analysis(df_raw, price_api_key=None):
    """
    Agent 2: Loads raw DataFrame, cleans it, enriches with Price API, 
    and returns a clean DataFrame and plots.
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

    # NEW: Enrich with Price API data
    df_cleaned = fetch_price_history_and_volatility(df_cleaned, price_api_key)

    # --- 4. Generate Generic Plots ---
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