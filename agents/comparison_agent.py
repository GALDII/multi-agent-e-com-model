import pandas as pd

def run_comparison(df_clean):
    """
    Agent 4: Loads clean data and returns THREE reports:
    1. Cheapest listings
    2. Source price summary
    3. Historical value report
    Ensures 'source' column exists for all reports.
    """
    print(f"🔄 [Agent 4: Comparator] Initializing...")
    
    # Initialize all three as empty in case we return early
    if df_clean.empty:
        print("❌ [Agent 4: Comparator] No clean data to compare.")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    print(f"📊 [Agent 4: Comparator] Processing {len(df_clean)} products...")
    
    # Ensure 'source' column exists
    if 'source' not in df_clean.columns and 'seller' in df_clean.columns:
        df_clean['source'] = df_clean['seller']
    elif 'source' not in df_clean.columns:
        df_clean['source'] = 'Unknown'

    # --- Report 1: Top 10 Cheapest Listings ---
    print("📊 [Agent 4: Comparator] Generating 'Cheapest Listings' report...")
    df_cheapest = df_clean.sort_values(by='price').head(10).copy()
    
    # Ensure columns exist before selecting them
    cols_to_keep = ['title', 'price', 'source', 'rating', 'reviews', 'link']
    available_cols = [c for c in cols_to_keep if c in df_cheapest.columns]
    df_cheapest = df_cheapest[available_cols]

    # --- Report 2: Source Price Report ---
    print("📊 [Agent 4: Comparator] Generating 'Source Price' report...")
    if 'source' in df_clean.columns:
        # Group by source and aggregate
        df_source_report = df_clean.groupby('source')['price'].agg(
            count='count',
            min_price='min',
            avg_price='mean',
            max_price='max'
        ).sort_values(by='min_price').reset_index()
        
        print(f"✅ [Agent 4: Comparator] Analyzed {len(df_source_report)} unique sources.")
    else:
        print("⚠️ [Agent 4: Comparator] 'source' column not found.")
        df_source_report = pd.DataFrame()

    # --- Report 3: Historical Value Report ---
    print("📊 [Agent 4: Comparator] Generating 'Historical Value' report...")
    
    # Check if we have the historical columns from Agent 2
    if 'historic_avg_price' in df_clean.columns:
        df_historic = df_clean.dropna(subset=['historic_avg_price']).copy()
        
        if not df_historic.empty:
            # Calculate savings percentage
            df_historic['historical_saving_%'] = (
                (df_historic['historic_avg_price'] - df_historic['price']) / 
                df_historic['historic_avg_price'].replace(0, 1)  # Avoid division by zero
            ) * 100
            
            # Calculate 24h change percentage
            if 'price_change_24h' in df_historic.columns:
                df_historic['24h_price_change_%'] = df_historic['price_change_24h'] * 100
            else:
                df_historic['24h_price_change_%'] = 0

            # Sort by savings (best deals first)
            df_historic_report = df_historic.sort_values(
                by='historical_saving_%', ascending=False
            ).head(10).copy()
            
            # Select columns safely
            hist_cols = ['title', 'source', 'price', 'historic_avg_price', 
                        'historical_saving_%', '24h_price_change_%', 'price_volatility', 'link']
            available_hist_cols = [c for c in hist_cols if c in df_historic_report.columns]
            df_historic_report = df_historic_report[available_hist_cols]
            
            print(f"✅ [Agent 4: Comparator] Generated historical report with {len(df_historic_report)} entries.")
        else:
            df_historic_report = pd.DataFrame()
            print("⚠️ [Agent 4: Comparator] No valid historical data after filtering.")
    else:
        df_historic_report = pd.DataFrame()
        print("ℹ️ [Agent 4: Comparator] Historical data not available (Price API not used).")

    print("✅ [Agent 4: Comparator] All comparison reports generated.")
    
    return df_cheapest, df_source_report, df_historic_report