def get_dynamic_thresholds(encoded_df):
    """
    Intelligent Mechanism 1: Auto-Thresholding.
    Adjusts minimum support based on the density/size of the dataset.
    """
    num_transactions = len(encoded_df)
    
    if num_transactions < 1000:
        return 0.03  # 3% support for smaller datasets
    elif num_transactions < 2500:
        return 0.02  # 2% support as data grows
    else:
        return 0.015 # 1.5% for massive datasets to catch niche trends

def calculate_bvs(rules_df):
    """
    Intelligent Mechanism 2: Custom Rule Scoring Model.
    Calculates the Bundle Viability Score (BVS) to rank recommendations.
    """
    if rules_df.empty:
        return rules_df
        
    # BVS heavily weighs Lift (true association) and Confidence
    rules_df['BVS_Score'] = (0.6 * rules_df['lift']) + (0.4 * rules_df['confidence'] * 5)
    
    # Sort by our custom score rather than just raw support
    return rules_df.sort_values(by='BVS_Score', ascending=False)