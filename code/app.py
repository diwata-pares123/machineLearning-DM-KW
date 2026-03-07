import streamlit as st
import pandas as pd
import random
import csv
import os
import requests
from utils.data_loader import load_and_encode
from engine.miner import mine_patterns

# --- Page Config ---
st.set_page_config(page_title="DataBlitz AI Backend", layout="wide", page_icon="🎮")
st.title("🎮 Nexus Gaming - AI E-Commerce Backend")
st.write("Next-Gen Market-Basket Analysis with Self-Learning and Groq-Powered AI.")

# --- Available Gaming Items & Image Placeholders ---
AVAILABLE_ITEMS = [
    "PlayStation 5 Console", "DualSense Wireless Controller", "Spider-Man 2 (PS5)", 
    "Nintendo Switch OLED", "Zelda: Tears of the Kingdom", "Switch Pro Controller",
    "Xbox Series X Console", "Halo Infinite (Xbox)", "Xbox Wireless Controller",
    "Mechanical Gaming Keyboard", "Wireless Gaming Mouse", "XL RGB Mousepad",
    "27-inch 144Hz Gaming Monitor", "Noise-Cancelling Gaming Headset", 
    "1TB NVMe SSD", "Ergonomic Gaming Chair"
]

IMAGE_MAP = {item: f"https://dummyimage.com/200x200/2c3e50/45f0d0&text={item.replace(' ', '+')}" for item in AVAILABLE_ITEMS}

# --- Sidebar: Groq API Key & Controls ---
st.sidebar.header("⚡ Groq AI Settings")
groq_api_key = st.sidebar.text_input("Enter Groq API Key:", type="password", help="Get yours at console.groq.com")

st.sidebar.markdown("---")
st.sidebar.header("⚙️ System Controls")
iteration = st.sidebar.radio(
    "Select Data Phase (Self-Learning Test):",
    ("Iteration 1: Regular Season", "Iteration 2: Holiday Rush", "Iteration 3: Esports Season")
)

if "Regular" in iteration:
    file_path = "../data/dataset_A_regular.csv"
elif "Holiday" in iteration:
    file_path = "../data/dataset_B_holiday.csv" 
else:
    file_path = "../data/dataset_C_esports.csv"

# --- Sidebar: Live POS Simulator ---
st.sidebar.markdown("---")
st.sidebar.subheader("🛒 Live POS Simulator")
new_basket = st.sidebar.multiselect("Customer buys:", AVAILABLE_ITEMS)

if st.sidebar.button("Submit Transaction"):
    if len(new_basket) == 0:
        st.sidebar.error("Add items first!")
    elif not os.path.exists(file_path):
        st.sidebar.error("Dataset not found.")
    else:
        new_tx_id = f"LIVE_{random.randint(1000, 9999)}"
        with open(file_path, 'a', newline='') as f:
            writer = csv.writer(f)
            for item in new_basket:
                writer.writerow([new_tx_id, item])
        st.sidebar.success("Transaction saved! Engine adapting...")
        st.rerun()

# --- Main Engine Execution ---
# Note: Ensure 'pip install mlxtend' was successful!
encoded_data = load_and_encode(file_path)

if encoded_data is None:
    st.error(f"Data file not found at {file_path}. Please run generate_data.py!")
else:
    with st.spinner("Mining patterns & generating business strategies..."):
        freq_items, rules, applied_threshold = mine_patterns(encoded_data)
        
    st.info(f"🧠 **Self-Learning Trigger:** Engine auto-adjusted Min Support to **{applied_threshold*100}%** based on dataset density.")
    
    if rules is not None and not rules.empty:
        display_rules = rules.copy()
        display_rules['antecedents'] = display_rules['antecedents'].apply(lambda x: ', '.join(list(x)))
        display_rules['consequents'] = display_rules['consequents'].apply(lambda x: ', '.join(list(x)))
        rules_text = display_rules[['antecedents', 'consequents', 'confidence', 'lift']].head(10).to_string()
    else:
        display_rules = pd.DataFrame()
        rules_text = "No rules available yet."

    tab1, tab2, tab3 = st.tabs(["🎮 E-Commerce Storefront", "🤖 AI Assistant & Smart Deals", "💼 Owner Action Plan"])

    # --- TAB 1: STOREFRONT ---
    with tab1:
        if not display_rules.empty:
            st.subheader("🔥 Homepage: Featured Bundles")
            top_rule = display_rules.iloc[0]
            ant_item = top_rule['antecedents'].split(', ')[0]
            con_item = top_rule['consequents'].split(', ')[0]
            
            col1, col2, col3 = st.columns([1, 0.2, 1])
            with col1:
                st.image(IMAGE_MAP.get(ant_item), caption=ant_item)
            with col2:
                st.markdown("<h1 style='text-align: center; margin-top: 50px;'>+</h1>", unsafe_allow_html=True)
            with col3:
                st.image(IMAGE_MAP.get(con_item), caption=con_item)
                
            st.success(f"**System Strategy:** {top_rule['Business_Action']}")
            st.dataframe(display_rules[['antecedents', 'consequents', 'support', 'confidence', 'lift', 'BVS_Score', 'Business_Action']].head(10), use_container_width=True)
        else:
            st.warning("No strong rules found.")

    # --- TAB 2: AI ASSISTANT & SMART DEALS ---
    with tab2:
        st.subheader("🤖 Nexus AI Assistant (Powered by Groq)")
        user_question = st.text_input("Customer Question:", placeholder="e.g., 'What are the specs of the PS5?'")
        
        if st.button("Ask AI"):
            if not groq_api_key:
                st.error("⚠️ Please enter a Groq API Key in the sidebar!")
            else:
                with st.spinner("Nexus is processing via Groq..."):
                    try:
                        # Groq REST API Configuration
                        url = "https://api.groq.com/openai/v1/chat/completions"
                        headers = {
                            "Authorization": f"Bearer {groq_api_key}",
                            "Content-Type": "application/json"
                        }
                        
                        system_prompt = f"""You are 'Nexus', an elite gaming tech expert. 
                        Live Market Basket Data: \n{rules_text}\n
                        1. Answer question briefly. 
                        2. Recommend the 'consequent' item if they ask about an 'antecedent' based on the data.
                        3. Mention the specific confidence percentage. 
                        4. Give promo code 'NEXUS-GROQ' for 15% off bundles today!"""
                        
                        payload = {
                            "model": "llama-3.3-70b-versatile",
                            "messages": [
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_question}
                            ]
                        }
                        
                        response = requests.post(url, json=payload, headers=headers)
                        
                        if response.status_code == 200:
                            # Parse Groq/OpenAI response format
                            result = response.json()['choices'][0]['message']['content']
                            st.success("🤖 " + result)
                        else:
                            st.error(f"Groq Error {response.status_code}: {response.text}")
                    except Exception as e:
                        st.error(f"System Error: {e}")

    # --- TAB 3: OWNER ACTION PLAN ---
    with tab3:
        st.subheader("💼 MBA Store Action Plan")
        if not display_rules.empty:
            st.markdown("### 📋 Today's Hardcoded Directives")
            for i, rule in display_rules.head(3).iterrows():
                st.markdown(f"**Action: {rule['Business_Action']}**")
                st.write(f"👉 Bundle **{rule['antecedents']}** with **{rule['consequents']}** (Lift: {rule['lift']:.2f}x)")
                st.markdown("---")
            
            st.markdown("### 🧠 AI Marketing Strategist")
            if st.button("Generate Strategy Campaign"):
                if not groq_api_key:
                    st.error("Please enter Groq API key in sidebar!")
                else:
                    with st.spinner("Consulting Groq Marketing Llama..."):
                        try:
                            url = "https://api.groq.com/openai/v1/chat/completions"
                            headers = {
                                "Authorization": f"Bearer {groq_api_key}",
                                "Content-Type": "application/json"
                            }
                            
                            strategy_prompt = f"Using this MBA data: {rules_text}, write a 3-step actionable marketing campaign for a gaming store owner."
                            
                            payload = {
                                "model": "llama-3.3-70b-versatile",
                                "messages": [{"role": "user", "content": strategy_prompt}]
                            }
                            
                            response = requests.post(url, json=payload, headers=headers)
                            
                            if response.status_code == 200:
                                st.info("📊 " + response.json()['choices'][0]['message']['content'])
                            else:
                                st.error(f"Groq Error: {response.text}")
                        except Exception as e:
                            st.error(f"System Error: {e}")
        else:
            st.warning("Not enough data to generate an action plan.")