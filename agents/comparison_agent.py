import pandas as pd

def run_comparison(df_clean):
    """
    Agent 4: Loads clean data and returns two generic reports:
    1. A report of the cheapest listings overall.
    2. A summary of prices grouped by seller.
    """
    print(f"🔄 [Agent 4: Comparator] Initializing...")
    
    if df_clean.empty:
        print("❌ [Agent 4: Comparator] No clean data to compare.")
        return pd.DataFrame(), pd.DataFrame()

    # --- Report 1: Top 10 Cheapest Listings ---
    print("📊 [Agent 4: Comparator] Generating 'Cheapest Listings' report...")
    df_cheapest = df_clean.sort_values(by='price').head(10)
    df_cheapest = df_cheapest[['title', 'price', 'seller', 'rating', 'reviews', 'link']]

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

    print("✅ [Agent 4: Comparator] Comparison reports generated.")
    return df_cheapest, df_seller_report