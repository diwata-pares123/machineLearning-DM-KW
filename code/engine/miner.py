import numpy as np
from mlxtend.frequent_patterns import fpgrowth, association_rules
from .intelligence import get_dynamic_thresholds, calculate_bvs

def mine_patterns(encoded_df):
    """Runs FP-Growth and extracts high-value business rules."""
    
    # 1. Ask the intelligence module for the best threshold (Self-Learning)
    min_sup = get_dynamic_thresholds(encoded_df)
    
    # 2. Run FP-Growth
    frequent_itemsets = fpgrowth(encoded_df, min_support=min_sup, use_colnames=True)
    
    if frequent_itemsets.empty:
        return None, None, min_sup
        
    # 3. Generate Association Rules
    # NOTE: mlxtend automatically calculates support, confidence, lift, leverage, and conviction here!
    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.1)
    
    # Clean up infinite values in Conviction (sometimes happens when confidence is exactly 1.0)
    # This prevents the app from crashing during the presentation
    rules.replace([np.inf, -np.inf], 999, inplace=True)
    
    # 4. Apply our custom intelligence scoring (BVS)
    scored_rules = calculate_bvs(rules)
    
    # 5. SMART FEATURE: Auto-Generate Promo Strategies
    # The machine reads the math and decides the business action
    scored_rules['Business_Action'] = scored_rules.apply(determine_promo, axis=1)
    
    # Sort by our custom score so the best rules are always at the top
    scored_rules = scored_rules.sort_values(by='BVS_Score', ascending=False)
    
    return frequent_itemsets, scored_rules, min_sup

def determine_promo(row):
    """Intelligent logic to convert MBA math into marketing actions."""
    if row['lift'] >= 1.5 and row['confidence'] >= 0.6:
        return "🔥 High Synergy: Bundle together for 10% off."
    elif row['support'] >= 0.15 and row['lift'] < 1.2:
        return "📦 High Traffic: Place items together on homepage, no discount."
    elif row['confidence'] >= 0.7:
        return "🎯 Sure Bet: Show as 'Frequently Bought Together' in cart pop-up."
    else:
        return "💡 Standard Cross-sell: Suggest below the main item."