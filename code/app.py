import streamlit as st
import pandas as pd
import random
import csv
import os
from utils.data_loader import load_and_encode
from engine.miner import mine_patterns

# --- Page Config ---
st.set_page_config(page_title="Lumina AI Engine", layout="wide")
st.title("✨ Lumina Skincare - AI Bundle Engine")
st.write("Market-Basket Analysis Backend with Self-Learning capabilities.")

# --- Available Skincare Items ---
AVAILABLE_ITEMS = [
    "Gentle Cleanser", "Foaming Cleanser", "Exfoliating Toner", "Hydrating Toner",
    "Vitamin C Serum", "Niacinamide Serum", "Hyaluronic Acid Serum", "Lightweight Moisturizer",
    "Heavy Ceramide Cream", "Mineral Sunscreen SPF 50", "Chemical Sunscreen SPF 50", 
    "Snail Mucin Essence", "Pimple Patches", "Clay Mask", "Sheet Mask", "Lip Sleeping Mask"
]

# --- Sidebar Controls: Data Iteration ---
st.sidebar.header("System Controls")
st.sidebar.write("Simulate the data iterations:")

iteration = st.sidebar.radio(
    "Select Iteration (Time Phase):",
    ("Iteration 1: Summer Data", "Iteration 2: Shift to Winter", "Iteration 3: Full Winter")
)

# Determine which file we are currently working with
file_path = None
if iteration == "Iteration 1: Summer Data":
    file_path = "../data/dataset_A_summer.csv"
elif iteration == "Iteration 2: Shift to Winter":
    file_path = "../data/dataset_B_transition.csv" 
elif iteration == "Iteration 3: Full Winter":
    file_path = "../data/dataset_C_winter.csv"

# --- Sidebar Controls: Live POS Simulator ---
st.sidebar.markdown("---")
st.sidebar.subheader("🛒 Live POS Simulator")
st.sidebar.write("Inject new data and watch the AI adapt in real-time.")

new_basket = st.sidebar.multiselect("Select items for checkout:", AVAILABLE_ITEMS)

if st.sidebar.button("Submit Transaction"):
    if len(new_basket) == 0:
        st.sidebar.error("Please add items to the basket first!")
    elif not os.path.exists(file_path):
        st.sidebar.error("Dataset not found. Please run the data generator first.")
    else:
        # Generate a random Transaction ID
        new_tx_id = f"LIVE_{random.randint(1000, 9999)}"
        
        # Open the CSV and append the new items
        with open(file_path, 'a', newline='') as f:
            writer = csv.writer(f)
            for item in new_basket:
                writer.writerow([new_tx_id, item])
                
        st.sidebar.success(f"Transaction {new_tx_id} saved! Engine updating...")
        # Automatically rerun the app to ingest the new data
        st.rerun()

# --- Main App Execution ---
st.markdown("### 📊 Engine Status")
encoded_data = load_and_encode(file_path)

if encoded_data is None:
    st.error(f"Data file not found at {file_path}. We need to generate the data first!")
else:
    st.success(f"Database currently holds **{len(encoded_data)}** transactions.")
    
    # Run the mining engine
    with st.spinner("Mining patterns and calculating BVS..."):
        freq_items, rules, applied_threshold = mine_patterns(encoded_data)
        
    st.info(f"🧠 **Self-Learning Trigger:** System auto-selected a Min Support of **{applied_threshold*100}%** based on data density.")
    
    if rules is not None and not rules.empty:
        st.markdown("---")
        st.subheader("🛍️ Homepage Widget: Top Bundle Recommendations")
        st.write("Ranked dynamically by our custom **Bundle Viability Score (BVS)**.")
        
        # Format outputs for presentation
        display_rules = rules[['antecedents', 'consequents', 'support', 'confidence', 'lift', 'BVS_Score']].head(5).copy()
        
        # Clean up the frozensets for display
        display_rules['antecedents'] = display_rules['antecedents'].apply(lambda x: ', '.join(list(x)))
        display_rules['consequents'] = display_rules['consequents'].apply(lambda x: ', '.join(list(x)))
        
        # Display the main table
        st.dataframe(display_rules, use_container_width=True)
        
        # Generate a business insight
        top_rule = display_rules.iloc[0]
        st.success(f"**Business Insight:** Customers buying **{top_rule['antecedents']}** are highly likely to buy **{top_rule['consequents']}**. Consider grouping these on the homepage for a 10% bundle discount!")

        # --- NEW SECTION: Cross-Sell Simulator ---
        st.markdown("---")
        st.subheader("🛒 Cart Pop-up: Cross-Sell Simulator")
        st.write("Simulate a user adding a single item to their cart to see what the engine recommends next.")
        
        col1, col2 = st.columns(2)
        with col1:
            cart_item = st.selectbox("Customer adds this to cart:", AVAILABLE_ITEMS)
            
        with col2:
            st.write("**Engine Recommends:**")
            # Filter the rules to find what consequents match the cart_item
            # We use frozenset({cart_item}) to match the exact format in the rules dataframe
            matching_rules = rules[rules['antecedents'] == frozenset({cart_item})]
            
            if not matching_rules.empty:
                # Get the highest BVS consequent
                best_match = list(matching_rules.iloc[0]['consequents'])
                confidence_val = round(matching_rules.iloc[0]['confidence'] * 100, 1)
                
                st.info(f"✨ **{', '.join(best_match)}**")
                st.caption(f"System Confidence: {confidence_val}%")
            else:
                st.write("No strong data for this item yet. Buy it to teach the engine!")
                
    else:
        st.warning("No strong rules found with the current data.")