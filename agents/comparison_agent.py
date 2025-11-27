import pandas as pd

def run_comparison(df_clean):
    """
    Agent 4: Loads clean data and returns THREE reports:
    1. Cheapest listings
    2. Seller price summary
    3. Historical value report (NEW)
    """
    print(f"🔄 [Agent 4: Comparator] Initializing...")
    
    # Initialize all three as empty in case we return early
    if df_clean.empty:
        print("❌ [Agent 4: Comparator] No clean data to compare.")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    # --- Report 1: Top 10 Cheapest Listings ---
    print("📊 [Agent 4: Comparator] Generating 'Cheapest Listings' report...")
    df_cheapest = df_clean.sort_values(by='price').head(10)
    # Ensure columns exist before selecting them
    cols_to_keep = ['title', 'price', 'seller', 'rating', 'reviews', 'link']
    df_cheapest = df_cheapest[[c for c in cols_to_keep if c in df_cheapest.columns]]

    # --- Report 2: Seller Price Report ---
    print("📊 [Agent 4: Comparator] Generating 'Seller Price' report...")
    if 'seller' in df_clean.columns:
        df_seller_report = df_clean.groupby('seller')['price'].agg(
            num_listings='count',
            min_price='min',
            avg_price='mean',
            max_price='max'
        ).sort_values(by='min_price').reset_index()
    else:
        df_seller_report = pd.DataFrame()

    # --- Report 3: Historical Value Report (The Missing Piece) ---
    print("📊 [Agent 4: Comparator] Generating 'Historical Value' report...")
    # Check if we actually have the new columns from Agent 2
    if 'historic_avg_price' in df_clean.columns:
        df_historic = df_clean.dropna(subset=['historic_avg_price']).copy()
        
        # Calculate savings
        df_historic['historical_saving_%'] = (
            (df_historic['historic_avg_price'] - df_historic['price']) / df_historic['historic_avg_price']
        ) * 100
        
        # Calculate 24h change
        if 'price_change_24h' in df_clean.columns:
            df_historic['24h_price_change_%'] = df_historic['price_change_24h'] * 100
        else:
            df_historic['24h_price_change_%'] = 0

        df_historic_report = df_historic.sort_values(by='historical_saving_%', ascending=False).head(10)
        
        # Select columns safely
        hist_cols = ['title', 'seller', 'price', 'historic_avg_price', 
                     'historical_saving_%', '24h_price_change_%', 'price_volatility', 'link']
        df_historic_report = df_historic_report[[c for c in hist_cols if c in df_historic_report.columns]]
    else:
        df_historic_report = pd.DataFrame()

    print("✅ [Agent 4: Comparator] Comparison reports generated.")
    
    # CRITICAL: This return statement must have 3 variables
    return df_cheapest, df_seller_report, df_historic_report