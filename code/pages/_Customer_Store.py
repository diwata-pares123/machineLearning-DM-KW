import streamlit as st
import pandas as pd
import requests
import csv
import os
import random
from utils.data_loader import load_and_encode
from engine.miner import mine_patterns

st.set_page_config(page_title="Nexus Storefront", layout="wide")

# 🖼️ YOUR EXACT PICTURE ROUTES
IMAGE_MAP = {
    "PlayStation 5 Console": "images/ps5_console.jpg",
    "DualSense Wireless Controller": "images/dualsense.jpg",
    "Spider-Man 2 (PS5)": "images/spiderman2.jpg",
    "Nintendo Switch OLED": "images/switch_oled.webp",
    "Zelda: Tears of the Kingdom": "images/zelda_totk.jpg",
    "Switch Pro Controller": "images/switch_pro.jpg",
    "Xbox Series X Console": "images/xbox_series_x.avif",
    "Halo Infinite (Xbox)": "images/halo_infinite.jpg",
    "Xbox Wireless Controller": "images/xbox_controller.jpg",
    "Mechanical Gaming Keyboard": "images/mech_keyboard.jpg",
    "Wireless Gaming Mouse": "images/wireless_mouse.jpg",
    "XL RGB Mousepad": "images/rgb_mousepad.jpg",
    "27-inch 144Hz Gaming Monitor": "images/144hz_monitor.jpg",
    "Noise-Cancelling Gaming Headset": "images/gaming_headset.jpg",
    "1TB NVMe SSD": "images/1tb_ssd.jpg",
    "Ergonomic Gaming Chair": "images/gaming_chair.jpg"
}

AVAILABLE_ITEMS = list(IMAGE_MAP.keys())

# --- MBA ENGINE (LOAD RULES) ---
encoded_data = load_and_encode(st.session_state.current_dataset)
raw_rules = pd.DataFrame()
unique_bundles = []
rules_text = ""

if encoded_data is not None:
    _, rules, _ = mine_patterns(encoded_data)
    if rules is not None and not rules.empty:
        raw_rules = rules.copy() # Keep a copy for Cart Suggestions
        
        # 🧠 DYNAMIC MULTI-ITEM BUNDLING (For Tab 1)
        seen_sets = set()
        for _, row in rules.sort_values(by='lift', ascending=False).iterrows():
            full_set = set(row['antecedents']) | set(row['consequents'])
            bundle_id = tuple(sorted(list(full_set)))
            if bundle_id not in seen_sets:
                unique_bundles.append({'items': list(full_set), 'lift': row['lift']})
                seen_sets.add(bundle_id)
        
        rules_text = rules[['antecedents', 'consequents']].head(10).to_string()
    else:
        rules_text = "No strong bundles today."

st.title("🛍️ Nexus Gaming Storefront")
tab1, tab2, tab3 = st.tabs(["🕹️ Browse & Shop", "🛒 My Cart & Checkout", "💬 AI Shopping Assistant"])

# --- TAB 1: SHOPPING & PROMO BUNDLES ---
with tab1:
    st.subheader("🔥 Top 3 AI Promo Bundles")
    if unique_bundles:
        # Limit to Top 3 and use columns for horizontal alignment
        num_to_display = min(len(unique_bundles), 3)
        bundle_cols = st.columns(3)
        
        for b_idx in range(num_to_display):
            items = unique_bundles[b_idx]['items']
            with bundle_cols[b_idx]:
                with st.container(border=True):
                    st.markdown(f"#### 🌟 Bundle Set #{b_idx+1}")
                    
                    # Align item images horizontally inside the card
                    item_sub_cols = st.columns(len(items))
                    for i, item_name in enumerate(items):
                        with item_sub_cols[i]:
                            try:
                                st.image(IMAGE_MAP[item_name], use_container_width=True)
                            except:
                                st.warning("📷")
                            st.caption(item_name)
                    
                    if st.button(f"Add Bundle #{b_idx+1}", key=f"b_btn_{b_idx}", use_container_width=True):
                        st.session_state.cart.extend(items)
                        st.rerun()
    else:
        st.info("The AI is analyzing market trends. Try back after more sales!")

    st.markdown("---")
    st.subheader("All Gaming Gear")
    grid_cols = st.columns(4)
    for i, item in enumerate(AVAILABLE_ITEMS): 
        with grid_cols[i % 4]:
            try:
                st.image(IMAGE_MAP[item], use_container_width=True)
            except:
                st.error(f"File Error: {item}")
            st.markdown(f"**{item}**")
            if st.button("Add to Cart", key=f"shop_item_{i}", use_container_width=True):
                st.session_state.cart.append(item)
                st.toast(f"Added {item}!")

# --- TAB 2: SMART CHECKOUT ---
with tab2:
    st.subheader("🛒 Your Shopping Cart")
    if not st.session_state.cart:
        st.info("Your cart is empty.")
    else:
        col_list, col_spacer, col_rec = st.columns([0.4, 0.1, 0.5])
        
        with col_list:
            for item in st.session_state.cart:
                st.write(f"✅ {item}")
            if st.button("🗑️ Empty Cart"):
                st.session_state.cart = []
                st.rerun()

        # 🧠 MBA REAL-TIME RECOMMENDATION LOGIC
        with col_rec:
            st.markdown("### 💡 Recommended for You")
            suggestions = set()
            if not raw_rules.empty:
                current_cart_set = set(st.session_state.cart)
                for _, row in raw_rules.iterrows():
                    # If any item in the cart matches the antecedent...
                    if set(row['antecedents']).issubset(current_cart_set):
                        # ...suggest the consequent (if not already in cart)
                        for potential in row['consequents']:
                            if potential not in current_cart_set:
                                suggestions.add(potential)
            
            if suggestions:
                st.write("Complete your setup with these popular pairings:")
                rec_cols = st.columns(min(len(suggestions), 2))
                for idx, rec_item in enumerate(list(suggestions)[:2]): # Show top 2 specific suggestions
                    with rec_cols[idx % 2]:
                        with st.container(border=True):
                            st.image(IMAGE_MAP[rec_item], width=100)
                            st.caption(rec_item)
                            if st.button(f"Add {rec_item}", key=f"rec_{idx}"):
                                st.session_state.cart.append(rec_item)
                                st.rerun()
            else:
                st.caption("No specific pairings found for your current items. Try adding more gear!")

        st.markdown("---")
        if st.button("💳 Proceed to Checkout", type="primary", use_container_width=True):
            new_tx_id = f"WEB_{random.randint(10000, 99999)}"
            with open(st.session_state.current_dataset, 'a', newline='') as f:
                writer = csv.writer(f)
                for item in st.session_state.cart:
                    writer.writerow([new_tx_id, item])
            st.success("Purchase successful! Live dataset updated.")
            st.session_state.cart = [] 
            st.rerun() 

# --- TAB 3: CUSTOMER AI ---
with tab3:
    st.subheader("🤖 Chat with Nexus")
    if "cust_messages" not in st.session_state:
        st.session_state.cust_messages = [{"role": "assistant", "content": "Welcome! Looking for gear?"}]

    chat_box = st.container(height=400)
    with chat_box:
        for m in st.session_state.cust_messages:
            with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Ask Nexus..."):
        if not st.session_state.groq_api_key:
            st.error("Set API Key on Home page.")
        else:
            st.session_state.cust_messages.append({"role": "user", "content": prompt})
            with chat_box:
                with st.chat_message("user"): st.markdown(prompt)
            
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "system", "content": f"You are Nexus. Suggest pairings based on: {rules_text}"}] + st.session_state.cust_messages
            }
            res = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                                headers={"Authorization": f"Bearer {st.session_state.groq_api_key}"}, json=payload)
            if res.status_code == 200:
                reply = res.json()['choices'][0]['message']['content']
                st.session_state.cust_messages.append({"role": "assistant", "content": reply})
                st.rerun()