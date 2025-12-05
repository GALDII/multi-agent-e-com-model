import pandas as pd
try:
    import requests
except ImportError:
    print("❌ requests library not found. Installing...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

def run_scraper(product_query, api_key):
    """
    Agent 1: Scraper Agent
    Scrapes product data from Google Shopping using SerpApi.
    Returns a DataFrame with product information.
    """
    print(f"🕵️ [Agent 1: Scraper] Initializing search for: '{product_query}'")
    
    if not api_key:
        print("❌ [Agent 1: Scraper] API key is required.")
        return pd.DataFrame()
    
    try:
        # Configure search parameters
        params = {
            "engine": "google_shopping",
            "q": product_query,
            "api_key": api_key,
            "num": 100,  # Get up to 100 results
            "gl": "in",  # India
            "hl": "en"
        }
        
        print("🔍 [Agent 1: Scraper] Querying Google Shopping API...")
        
        # Make API request
        url = "https://serpapi.com/search"
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        results = response.json()
        
        # Extract shopping results
        shopping_results = results.get("shopping_results", [])
        
        if not shopping_results:
            print("⚠️ [Agent 1: Scraper] No results found.")
            print(f"ℹ️ [Agent 1: Scraper] API Response keys: {list(results.keys())}")
            
            # Check if there's an error message
            if 'error' in results:
                print(f"❌ [Agent 1: Scraper] API Error: {results['error']}")
            
            return pd.DataFrame()
        
        print(f"✅ [Agent 1: Scraper] Found {len(shopping_results)} products.")
        
        # Parse results into structured data
        products = []
        for item in shopping_results:
            # Extract price - handle different formats
            price = 0
            if 'extracted_price' in item:
                price = item['extracted_price']
            elif 'price' in item:
                price_str = str(item['price']).replace('₹', '').replace(',', '').strip()
                try:
                    price = float(price_str)
                except:
                    price = 0
            
            product = {
                'title': item.get('title', 'N/A'),
                'price': price,
                'source': item.get('source', 'Unknown'),
                'seller': item.get('source', 'Unknown'),
                'link': item.get('link', ''),
                'rating': item.get('rating', None),
                'reviews': item.get('reviews', 0),
                'product_id': item.get('product_id', ''),
                'thumbnail': item.get('thumbnail', ''),
                'delivery': item.get('delivery', 'N/A')
            }
            products.append(product)
        
        df = pd.DataFrame(products)
        print(f"📊 [Agent 1: Scraper] Successfully scraped {len(df)} products.")
        print(f"📋 [Agent 1: Scraper] Columns: {df.columns.tolist()}")
        
        # Show price range
        valid_prices = df[df['price'] > 0]['price']
        if not valid_prices.empty:
            print(f"💰 [Agent 1: Scraper] Price range: ₹{valid_prices.min():.2f} - ₹{valid_prices.max():.2f}")
        
        return df
        
    except Exception as e:
        print(f"❌ [Agent 1: Scraper] Error during scraping: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        print(traceback.format_exc())
        return pd.DataFrame()