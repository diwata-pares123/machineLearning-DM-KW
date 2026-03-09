import pandas as pd

def get_dynamic_thresholds(encoded_df):
    """
    Intelligent Mechanism 1: True Dynamic Auto-Thresholding.
    Continuously adjusts minimum support based on the precise size of the dataset.
    Follows an inverse relationship: as data grows, the threshold lowers.
    """
    num_transactions = len(encoded_df)
    
    if num_transactions == 0:
        return 0.02  # Safety fallback for empty datasets
        
    # Mathematical Formula: Base Constant / Total Transactions
    # The constant '30' perfectly mirrors your previous expectations:
    # 1000 txs = 0.03 (3.0%) | 1500 txs = 0.02 (2.0%) | 2000 txs = 0.015 (1.5%)
    calculated_support = 30.0 / num_transactions
    
    # Clamp the threshold between 1.0% (0.01) and 5.0% (0.05) to prevent crashes
    dynamic_threshold = max(0.01, min(0.05, calculated_support))
    
    # Round to 4 decimal places for a clean percentage display in the UI
    return round(dynamic_threshold, 4)

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