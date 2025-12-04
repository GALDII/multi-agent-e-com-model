import pandas as pd
import matplotlib.pyplot as plt
import requests
import numpy as np

# --- 1. Generic Helper Functions ---
def clean_data(df):
    """Cleans the price, reviews, and rating columns."""
    df['price'] = df['price'].astype(str).str.replace(r'[₹,]', '', regex=True)
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    
    df['reviews'] = df['reviews'].astype(str).str.replace(r',', '', regex=True)
    df['reviews'] = pd.to_numeric(df['reviews'], errors='coerce').fillna(0).astype(int)
    
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    
    # Drop any rows where price is missing
    df = df.dropna(subset=['price'])
    
    # Ensure both 'source' and 'seller' columns exist
    if 'source' in df.columns and 'seller' not in df.columns:
        df['seller'] = df['source']
    elif 'seller' in df.columns and 'source' not in df.columns:
        df['source'] = df['seller']
    
    return df

# --- 2. Price API Logic ---
def fetch_price_history_and_volatility(df_clean, price_api_key):
    """
    Agent Sub-function: Fetches historic data.
    If a key is provided, it tries to fetch real data.
    Otherwise (or if fetch fails), it falls back to simulation.
    """
    print("⏳ [Agent 2: Analyst] Processing Price History...")
    
    # Limiting to top 5 items to save API credits
    df_subset = df_clean.head(5).copy() 
    
    historic_avgs = []
    volatilities = []
    changes_24h = []

    for index, row in df_subset.iterrows():
        current_price = row['price']
        
        # --- SIMULATION LOGIC (Default) ---
        historic_prices = np.random.normal(loc=current_price, scale=current_price*0.05, size=7)
        avg_price = np.mean(historic_prices)
        volatility = np.std(historic_prices) / avg_price if avg_price > 0 else 0
        change = (current_price - historic_prices[-2]) / historic_prices[-2] if historic_prices[-2] > 0 else 0

        # --- REAL API LOGIC (Enable when ready) ---
        if price_api_key:
            try:
                url = "https://serpapi.com/search.json"
                payload = {'token': price_api_key, 'url': row['link']}
                response = requests.get(url, params=payload, timeout=10)
                data = response.json()
                 
                if 'average_price' in data:
                    avg_price = data['average_price']
                if 'volatility' in data:
                    volatility = data['volatility']
                if 'change_percentage' in data:
                    change = data['change_percentage']
            except Exception as e:
                print(f"⚠️ [Agent 2] API Error for {row.get('title', 'Unknown')}: {e}")
                # Keep simulation values
        
        historic_avgs.append(avg_price)
        volatilities.append(volatility)
        changes_24h.append(change)

    # Assign new columns to the subset
    df_subset['historic_avg_price'] = historic_avgs
    df_subset['price_volatility'] = volatilities
    df_subset['price_change_24h'] = changes_24h
    
    # Merge the enriched data back
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

    # Enrich with Price API data
    df_cleaned = fetch_price_history_and_volatility(df_cleaned, price_api_key)

    # --- 4. Generate Generic Plots ---
    print("📊 [Agent 2: Analyst] Generating visualizations...")
    plots = {}

    # A. Price Distribution Histogram
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(df_cleaned['price'], bins=30, edgecolor='black', alpha=0.7, color='#667eea')
        ax.set_title('Overall Price Distribution', fontsize=14, fontweight='bold')
        ax.set_xlabel('Price (₹)', fontsize=12)
        ax.set_ylabel('Frequency', fontsize=12)
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plots['price_histogram'] = fig
    except Exception as e:
        print(f"⚠️ [Agent 2: Analyst] Histogram generation failed: {e}")

    # B. Price vs. Rating Scatter
    df_rated = df_cleaned.dropna(subset=['rating'])
    if not df_rated.empty:
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            scatter_sizes = df_rated['reviews'].clip(upper=1000) / 10
            ax.scatter(df_rated['rating'], df_rated['price'], alpha=0.6, 
                      s=scatter_sizes, c='#764ba2', edgecolors='white', linewidth=0.5)
            ax.set_title('Price vs. Rating (Size by Review Count)', fontsize=14, fontweight='bold')
            ax.set_xlabel('Rating (1-5)', fontsize=12)
            ax.set_ylabel('Price (₹)', fontsize=12)
            ax.grid(True, linestyle='--', alpha=0.5)
            plt.tight_layout()
            plots['price_vs_rating_scatter'] = fig
        except Exception as e:
            print(f"⚠️ [Agent 2: Analyst] Scatter plot generation failed: {e}")

    # C. Top Sellers Bar Chart
    seller_col = 'source' if 'source' in df_cleaned.columns else 'seller'
    if seller_col in df_cleaned.columns:
        try:
            fig, ax = plt.subplots(figsize=(10, 7))
            seller_counts = df_cleaned[seller_col].value_counts().nlargest(15).sort_values()
            seller_counts.plot(kind='barh', ax=ax, color='#667eea')
            ax.set_title('Top 15 Sellers by Number of Listings', fontsize=14, fontweight='bold')
            ax.set_xlabel('Number of Listings', fontsize=12)
            ax.grid(axis='x', linestyle='--', alpha=0.5)
            plt.tight_layout()
            plots['top_sellers_bar'] = fig
        except Exception as e:
            print(f"⚠️ [Agent 2: Analyst] Bar chart generation failed: {e}")
    
    print(f"✅ [Agent 2: Analyst] Analysis complete. Generated {len(plots)} visualizations.")
    return df_cleaned, plots