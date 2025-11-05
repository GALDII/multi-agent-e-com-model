import pandas as pd
import matplotlib.pyplot as plt
import re

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

    # --- 3. Generate Generic Plots ---
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