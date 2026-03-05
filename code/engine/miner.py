from mlxtend.frequent_patterns import fpgrowth, association_rules
from .intelligence import get_dynamic_thresholds, calculate_bvs

def mine_patterns(encoded_df):
    """Runs FP-Growth and extracts high-value business rules."""
    
    # 1. Ask the intelligence module for the best threshold
    min_sup = get_dynamic_thresholds(encoded_df)
    
    # 2. Run FP-Growth
    frequent_itemsets = fpgrowth(encoded_df, min_support=min_sup, use_colnames=True)
    
    if frequent_itemsets.empty:
        return None, None, min_sup
        
    # 3. Generate Association Rules (Calculate Confidence, Lift, etc.)
    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.1)
    
    # 4. Apply our custom intelligence scoring
    scored_rules = calculate_bvs(rules)
    
    return frequent_itemsets, scored_rules, min_sup