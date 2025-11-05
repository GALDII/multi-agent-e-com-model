import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

def run_prediction(df_clean):
    """
    Agent 3: Loads clean data, builds a GENERIC price prediction model,
    and returns feature importance and potential deals DataFrames.
    """
    print(f"🤖 [Agent 3: Predictor] Initializing...")
    
    # --- 1. Use Generic Features ---
    # We predict price based on who is selling it and its reputation
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
        
        # We only care about the top 15 most important features
        feature_importance_df = feature_importance_df.head(15)

    except Exception:
        feature_importance_df = pd.DataFrame(columns=['feature', 'importance'])

    # --- 5. Find Deals (this logic is still valid and useful) ---
    predictions = model.predict(X)
    df_model['predicted_price'] = predictions
    df_model['price_difference'] = df_model['predicted_price'] - df_model['price']
    
    deals_df = df_model.sort_values(by='price_difference', ascending=False)
    deals_df = deals_df[['title', 'seller', 'price', 'predicted_price', 'price_difference', 'link']]
    
    print("✅ [Agent 3: Predictor] Predictions and importances generated.")
    return feature_importance_df, deals_df