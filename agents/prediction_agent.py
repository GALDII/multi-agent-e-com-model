import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

def run_prediction(df_clean):
    """
    Agent 3: Loads clean data, builds a price prediction model,
    and returns feature importance and potential deals DataFrames.
    """
    print(f"🤖 [Agent 3: Predictor] Initializing...")
    
    # Ensure both 'source' and 'seller' columns exist
    if 'source' in df_clean.columns and 'seller' not in df_clean.columns:
        df_clean['seller'] = df_clean['source']
    elif 'seller' in df_clean.columns and 'source' not in df_clean.columns:
        df_clean['source'] = df_clean['seller']
    
    # --- 1. Use Generic Features ---
    features = ['seller', 'rating', 'reviews']
    target = 'price'

    # Remove rows where these key features are missing
    df_model = df_clean.dropna(subset=features + [target]).copy()
    
    if df_model.empty or len(df_model) < 5:
        print("❌ [Agent 3: Predictor] Not enough complete data (seller, rating, reviews, price) to build a model.")
        return pd.DataFrame(), pd.DataFrame()
        
    X = df_model[features]
    y = df_model[target]

    # --- 2. Build Preprocessing Pipeline ---
    categorical_features = ['seller']
    numeric_features = ['rating', 'reviews']
    
    numeric_transformer = Pipeline(steps=[('imputer', SimpleImputer(strategy='mean'))])
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])
    
    # --- 3. Define and Train Model ---
    model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
    ])

    try:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        if X_train.empty:
            print("❌ [Agent 3: Predictor] Not enough data to train model after split.")
            return pd.DataFrame(), pd.DataFrame()
        
        model.fit(X_train, y_train)
        print("🧠 [Agent 3: Predictor] Model training complete.")
    except Exception as e:
        print(f"❌ [Agent 3: Predictor] Model training failed: {e}")
        return pd.DataFrame(), pd.DataFrame()

    # --- 4. Get Feature Importances ---
    try:
        ohe_features = model.named_steps['preprocessor'].named_transformers_['cat'] \
                            .named_steps['onehot'].get_feature_names_out(categorical_features)
        all_feature_names = numeric_features + list(ohe_features)
        importances = model.named_steps['regressor'].feature_importances_
        
        feature_importance_df = pd.DataFrame({
            'feature': all_feature_names,
            'importance': importances
        }).sort_values(by='importance', ascending=False)
        
        feature_importance_df = feature_importance_df.head(15)

    except Exception as e:
        print(f"⚠️ [Agent 3: Predictor] Feature importance extraction failed: {e}")
        feature_importance_df = pd.DataFrame(columns=['feature', 'importance'])

    # --- 5. Find Deals ---
    try:
        predictions = model.predict(X)
        df_model['predicted_price'] = predictions
        df_model['price_difference'] = df_model['predicted_price'] - df_model['price']
        
        # Ensure 'source' column exists in deals_df
        deals_df = df_model.sort_values(by='price_difference', ascending=False).copy()
        
        # Select columns safely - use what's available
        cols_to_include = ['title', 'price', 'predicted_price', 'price_difference']
        
        # Add source column
        if 'source' in deals_df.columns:
            cols_to_include.append('source')
        elif 'seller' in deals_df.columns:
            deals_df['source'] = deals_df['seller']
            cols_to_include.append('source')
        
        # Add link if available
        if 'link' in deals_df.columns:
            cols_to_include.append('link')
        
        deals_df = deals_df[cols_to_include]
        
        print(f"✅ [Agent 3: Predictor] Generated {len(deals_df)} predictions. Columns: {deals_df.columns.tolist()}")
    except Exception as e:
        print(f"❌ [Agent 3: Predictor] Deal generation failed: {e}")
        deals_df = pd.DataFrame(columns=['title', 'price', 'predicted_price', 'price_difference', 'source'])
    
    return feature_importance_df, deals_df