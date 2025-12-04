import serpapi
import pandas as pd

def run_scraper(product_query, api_key):
    """
    Agent 1: Scrapes Google Shopping data and returns a DataFrame.
    Modified to also look for a common unique ID or just use the link as ID.
    """
    print(f"🕵️ [Agent 1: Scraper] Initializing... Searching for '{product_query}'")
    params = {
        "engine": "google_shopping", "q": product_query, "api_key": api_key,
        "google_domain": "google.co.in", "gl": "in", "hl": "en"
    }
    
    try:
        search = serpapi.search(params)
        results = search.as_dict()
        if "shopping_results" not in results:
            print("❌ [Agent 1: Scraper] No shopping results found.")
            return pd.DataFrame()

        shopping_results = results["shopping_results"]
        print(f"✅ [Agent 1: Scraper] Found {len(shopping_results)} products.")
        
        products_data = []
        for item in shopping_results:
            products_data.append({
                'title': item.get('title'), 
                'price': item.get('price'),
                'seller': item.get('source'), 
                'rating': item.get('rating'),
                'reviews': item.get('reviews'), 
                'link': item.get('link'),
                'delivery': item.get('delivery'),
                'product_identifier': item.get('link') 
            })
            
        if not products_data:
            print("❌ [Agent 1: Scraper] No data was extracted.")
            return pd.DataFrame()
            
        print(f"✅ [Agent 1: Scraper] Data successfully scraped.")
        return pd.DataFrame(products_data)

    except Exception as e:
        print(f"❌ [Agent 1: Scraper] An error occurred: {e}")
        return pd.DataFrame()