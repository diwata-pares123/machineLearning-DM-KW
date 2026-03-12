import streamlit as st
import pandas as pd
import requests
import csv
import os
import random
from utils.data_loader import load_and_encode
from engine.miner import mine_patterns

st.set_page_config(page_title="Nexus Storefront", layout="wide")

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
        raw_rules = rules.copy()
        
        seen_sets = set()
        for _, row in rules.sort_values(by='lift', ascending=False).iterrows():
            full_set = set(row['antecedents']) | set(row['consequents'])
            bundle_id = tuple(sorted(list(full_set)))
            if bundle_id not in seen_sets:
                unique_bundles.append({'items': list(full_set), 'lift': row['lift']})
                seen_sets.add(bundle_id)
        
        # --- NEW: Format rules into plain English for the AI ---
        for _, row in rules.sort_values(by='lift', ascending=False).head(5).iterrows():
            ant = ', '.join(list(row['antecedents']))
            con = ', '.join(list(row['consequents']))
            rules_text += f"- AI Bundle Alert: If the user buys {ant}, strongly recommend {con}!\n"
    else:
        rules_text = "No strong bundles today."

st.title("🛍️ Nexus Gaming Storefront")
tab1, tab2, tab3 = st.tabs(["🕹️ Browse & Shop", "🛒 My Cart & Checkout", "💬 AI Shopping Assistant"])

# --- TAB 1: SHOPPING & PROMO BUNDLES ---
with tab1:
    st.subheader("🔥 Top AI Promo Bundles")
    if unique_bundles:
        num_to_display = min(len(unique_bundles), 3)
        bundle_cols = st.columns(3)
        
        for b_idx in range(num_to_display):
            items = unique_bundles[b_idx]['items']
            with bundle_cols[b_idx]:
                with st.container(border=True):
                    st.markdown(f"#### 🌟 Bundle Set #{b_idx+1}")
                    item_sub_cols = st.columns(len(items))
                    for i, item_name in enumerate(items):
                        with item_sub_cols[i]:
                            try: st.image(IMAGE_MAP[item_name], use_container_width=True)
                            except: st.warning("📷")
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
            try: st.image(IMAGE_MAP[item], use_container_width=True)
            except: st.error("Image Error")
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
            # Item-by-item deletion in Cart
            st.write("Review your items:")
            for idx, item in enumerate(st.session_state.cart):
                c1, c2 = st.columns([0.8, 0.2])
                c1.write(f"✅ {item}")
                if c2.button("❌", key=f"del_cart_{idx}"):
                    st.session_state.cart.pop(idx)
                    st.rerun()
            
            if st.button("🗑️ Empty Entire Cart", use_container_width=True):
                st.session_state.cart = []
                st.rerun()

        # 🧠 MBA REAL-TIME RECOMMENDATION LOGIC (WITH ML PROMOS)
        with col_rec:
            st.markdown("### 💡 AI Smart Offers")
            suggestions = {}
            if not raw_rules.empty:
                current_cart_set = set(st.session_state.cart)
                for _, row in raw_rules.iterrows():
                    if set(row['antecedents']).issubset(current_cart_set):
                        for potential in row['consequents']:
                            if potential not in current_cart_set:
                                # Save the item AND the ML-generated promo text
                                promo_text = row.get('Business_Action', "Pairs perfectly with your current cart!")
                                suggestions[potential] = promo_text
            
            if suggestions:
                st.write("Based on your cart, we recommend:")
                rec_cols = st.columns(min(len(suggestions), 2))
                for idx, (rec_item, promo_text) in enumerate(list(suggestions.items())[:2]): 
                    with rec_cols[idx % 2]:
                        with st.container(border=True):
                            try: st.image(IMAGE_MAP[rec_item], width=100)
                            except: st.warning("📷")
                            st.caption(f"**{rec_item}**")
                            # Display the AI's marketing strategy directly to the user!
                            st.info(promo_text) 
                            if st.button(f"Add {rec_item}", key=f"rec_{idx}"):
                                st.session_state.cart.append(rec_item)
                                st.rerun()
            else:
                st.caption("No specific pairings found. Try adding more gear!")

        st.markdown("---")
        if st.button("💳 Proceed to Checkout", type="primary", use_container_width=True):
            # PREPROCESSING: Remove duplicates from cart using set() before saving
            clean_cart = list(set([item.strip() for item in st.session_state.cart if item.strip()]))
            
            # --- 🔍 LIVE AUDIT TRAIL CAPTURE ---
            st.session_state.demo_raw_cart = st.session_state.cart.copy()
            st.session_state.demo_clean_cart = clean_cart.copy()
            # -----------------------------------

            new_tx_id = f"WEB_{random.randint(10000, 99999)}"
            with open(st.session_state.current_dataset, 'a', newline='') as f:
                writer = csv.writer(f)
                for item in clean_cart:
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
            
            # --- 🧠 PREPARE DATA FOR CUSTOMER AI ---
            current_cart_str = ", ".join(st.session_state.cart) if st.session_state.cart else "Cart is currently empty."
            
            bestsellers_text = "Data currently loading..."
            if not raw_rules.empty:
                top_ants_df = raw_rules.groupby('antecedents')['support'].max().sort_values(ascending=False).head(3)
                bestsellers_text = top_ants_df.to_string()

            # --- 🛑 UPDATED STRICT CUSTOMER PROMPT ---
            system_prompt = f"""
            You are Nexus, the friendly AI Shopping Assistant and virtual salesperson of the Nexus Gaming Store.
            
            USER'S CURRENT CART: {current_cart_str}
            
            STORE BESTSELLERS (Most Purchased Items):
            {bestsellers_text}
            
            🔥 TODAY'S ACTIVE AI PROMO BUNDLES 🔥
            {rules_text}
            
            STRICT INSTRUCTIONS: 
            1. NEVER say "we don't have pre-defined bundles." You MUST enthusiastically recommend the pairings listed in the "TODAY'S ACTIVE AI PROMO BUNDLES" section.
            2. If the user asks what is on sale or what is bundled, pitch the bundles from the list above.
            3. If the user has an item in their cart, check if it matches a bundle and aggressively (but politely) suggest the pairing!
            4. Never invent or guess metrics. Stay strictly grounded in the data provided.
            """
            
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "system", "content": system_prompt}] + st.session_state.cust_messages
            }
            res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers={"Authorization": f"Bearer {st.session_state.groq_api_key}"}, json=payload)
            if res.status_code == 200:
                reply = res.json()['choices'][0]['message']['content']
                st.session_state.cust_messages.append({"role": "assistant", "content": reply})
                st.rerun()