# comparison_agent.py

import pandas as pd

def run_comparison(df_clean):
    """
    Agent 4: Loads clean data and returns reports.
    New Report 3: Current Price vs. Historic Average.
    """
    print(f"🔄 [Agent 4: Comparator] Initializing...")
    
    if df_clean.empty:
        print("❌ [Agent 4: Comparator] No clean data to compare.")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame() # Added a third return
    
    # --- Report 1: Top 10 Cheapest Listings ---
    # ... (Existing logic remains the same) ...
    print("📊 [Agent 4: Comparator] Generating 'Cheapest Listings' report...")
    df_cheapest = df_clean.sort_values(by='price').head(10)
    df_cheapest = df_cheapest[['title', 'price', 'seller', 'rating', 'reviews', 'link']]

    # --- Report 2: Seller Price Report ---
    # ... (Existing logic remains the same) ...
    print("📊 [Agent 4: Comparator] Generating 'Seller Price' report...")
    if 'seller' in df_clean.columns:
        df_seller_report = df_clean.groupby('seller')['price'].agg(
            num_listings='count', min_price='min', avg_price='mean', max_price='max'
        ).sort_values(by='min_price').reset_index()
    else:
        df_seller_report = pd.DataFrame()

    # --- NEW Report 3: Historical Value Report ---
    print("📊 [Agent 4: Comparator] Generating 'Historical Value' report...")
    if 'historic_avg_price' in df_clean.columns:
        df_historic = df_clean.dropna(subset=['historic_avg_price']).copy()
        
        # Calculate the historical saving percentage
        df_historic['historical_saving_%'] = (
            (df_historic['historic_avg_price'] - df_historic['price']) / df_historic['historic_avg_price']
        ) * 100

        # Also indicate the 24h price movement
        df_historic['24h_price_change_%'] = df_historic['price_change_24h'] * 100
        
        df_historic_report = df_historic.sort_values(by='historical_saving_%', ascending=False).head(10)
        df_historic_report = df_historic_report[[
            'title', 'seller', 'price', 'historic_avg_price', 'historical_saving_%', 
            '24h_price_change_%', 'price_volatility', 'link'
        ]]
    else:
        df_historic_report = pd.DataFrame()
    
    print("✅ [Agent 4: Comparator] Comparison reports generated.")
    return df_cheapest, df_seller_report, df_historic_report # Return the new report