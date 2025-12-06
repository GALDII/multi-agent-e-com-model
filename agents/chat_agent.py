import pandas as pd
import os
try:
    from groq import Groq
except ImportError:
    pass # Handle in app.py if missing

def prepare_context(clean_data, deals_df, cheapest_df):
    """
    Converts the analyzed dataframes into a text summary for the AI.
    """
    if clean_data.empty:
        return "No market data available yet."

    stats = {
        "total_items": len(clean_data),
        "average_price": clean_data['price'].mean(),
        "lowest_price": clean_data['price'].min(),
        "highest_price": clean_data['price'].max(),
    }

    # Format Top 5 Deals
    deals_text = ""
    if not deals_df.empty:
        for _, row in deals_df.head(5).iterrows():
            deals_text += f"- {row['title']} at ₹{row['price']} (Save ₹{row['price_difference']:.2f}, Seller: {row.get('source', 'N/A')})\n"
    
    # Format Top 3 Cheapest
    cheap_text = ""
    if not cheapest_df.empty:
        for _, row in cheapest_df.head(3).iterrows():
            cheap_text += f"- {row['title']} at ₹{row['price']} (Seller: {row.get('source', 'N/A')})\n"

    context = f"""
    MARKET ANALYSIS CONTEXT:
    - Total Items Scanned: {stats['total_items']}
    - Market Average Price: ₹{stats['average_price']:.2f}
    - Lowest Price Found: ₹{stats['lowest_price']:.2f}
    
    TOP RECOMMENDED DEALS (Undervalued):
    {deals_text}
    
    LOWEST ABSOLUTE PRICES:
    {cheap_text}
    """
    return context

def get_ai_response(user_query, context, api_key, chat_history):
    """
    Sends the user query + data context to Groq.
    """
    if not api_key:
        return "⚠️ Please enter your Groq API Key in the sidebar to use the Chatbot."

    client = Groq(api_key=api_key)
    
    system_prompt = f"""You are 'Nexus AI', an expert shopping assistant. 
    You have access to real-time market data provided below.
    
    {context}
    
    RULES:
    1. Answer specifically based on the provided data.
    2. If the user asks for the "best deal", refer to the 'TOP RECOMMENDED DEALS' section.
    3. If the user asks for the "cheapest", refer to the 'LOWEST ABSOLUTE PRICES'.
    4. Keep answers concise, professional, and helpful.
    5. All prices are in INR (₹).
    """

    messages = [{"role": "system", "content": system_prompt}]
    
    # Add recent history (last 4 messages) for conversation flow
    for msg in chat_history[-4:]:
        messages.append(msg)
    
    messages.append({"role": "user", "content": user_query})

    try:
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama3-70b-8192", # Using Llama 3 on Groq for speed
            temperature=0.5,
            max_tokens=500,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"❌ Error communicating with AI: {str(e)}"