import streamlit as st
import pandas as pd
import random
import csv
import os
import requests
from utils.data_loader import load_and_encode
from engine.miner import mine_patterns

st.set_page_config(page_title="Nexus Admin Back-Office", layout="wide")

AVAILABLE_ITEMS = [
    "PlayStation 5 Console", "DualSense Wireless Controller", "Spider-Man 2 (PS5)", 
    "Nintendo Switch OLED", "Zelda: Tears of the Kingdom", "Switch Pro Controller",
    "Xbox Series X Console", "Halo Infinite (Xbox)", "Xbox Wireless Controller",
    "Mechanical Gaming Keyboard", "Wireless Gaming Mouse", "XL RGB Mousepad",
    "27-inch 144Hz Gaming Monitor", "Noise-Cancelling Gaming Headset", 
    "1TB NVMe SSD", "Ergonomic Gaming Chair"
]

st.title("💼 Admin Back-Office & Analytics")
st.caption(f"Currently Analyzing Data Phase: `{st.session_state.current_dataset.split('/')[-1]}`")

tab1, tab2, tab3 = st.tabs(["📊 Live MBA Analytics", "🛒 Live POS Simulator", "🤖 AI Data Strategist"])

# --- TAB 1: ANALYTICS ---
with tab1:
    st.subheader("🧮 Engine Status & Rule Metrics")
    encoded_data = load_and_encode(st.session_state.current_dataset)
    display_rules = pd.DataFrame()
    
    if encoded_data is not None:
        freq_items, rules, applied_threshold = mine_patterns(encoded_data)
        st.info(f"Engine auto-adjusted Min Support to **{applied_threshold*100}%** based on dataset density.")
        
        if rules is not None and not rules.empty:
            display_rules = rules.copy()
            display_rules['antecedents'] = display_rules['antecedents'].apply(lambda x: ', '.join(list(x)))
            display_rules['consequents'] = display_rules['consequents'].apply(lambda x: ', '.join(list(x)))
            rules_text = display_rules[['antecedents', 'consequents', 'support', 'confidence', 'lift']].head(10).to_string()
            
            # Visuals 
            cA, cB = st.columns(2)
            with cA:
                st.write("**Confidence vs. Lift**")
                st.scatter_chart(display_rules[['confidence', 'lift']], x='confidence', y='lift')
            with cB:
                st.write("**Top Antecedents by Support**")
                bar_data = display_rules.groupby('antecedents')['support'].max().sort_values(ascending=False).head(5)
                st.bar_chart(bar_data)
        else:
            rules_text = "No strong rules found."
            st.warning("No patterns detected in this dataset.")

    if not display_rules.empty:
        st.markdown("---")
        st.subheader("📋 Full Market Basket Rules Table")
        
        # FIX: Drop the advanced metrics you haven't learned yet to keep the defense simple!
        cols_to_drop = ['zhangs_metric', 'jaccard', 'certainty', 'kulczynski', 'BVS_Score']
        clean_rules = display_rules.drop(columns=cols_to_drop, errors='ignore')

        # Render the clean table spanning the whole width
        st.dataframe(
            clean_rules.style.highlight_max(subset=['lift'], axis=0, color='#1e3a8a'), 
            use_container_width=True, 
            height=400
        )

# --- TAB 2: POS SIMULATOR (REAL-TIME) ---
# --- TAB 2: POS SIMULATOR (REAL-TIME) ---
with tab2:
    st.subheader("🛒 Point of Sale Simulator")
    st.write("Inject live transactions into the active dataset to force the engine to adapt.")
    
    # 1. Define the Callback Function that runs WHEN the button is clicked
    def process_transaction():
        # Grab the items from the widget's memory
        basket = st.session_state.pos_basket
        
        if len(basket) > 0 and os.path.exists(st.session_state.current_dataset):
            # Save the transaction
            new_tx_id = f"POS_LIVE_{random.randint(1000, 9999)}"
            with open(st.session_state.current_dataset, 'a', newline='') as f:
                writer = csv.writer(f)
                for item in basket:
                    writer.writerow([new_tx_id, item])
            
            # Clear the box and trigger the success message
            st.session_state.pos_basket = [] 
            st.session_state.tx_success = True 
        else:
            st.session_state.tx_error = True

    # 2. Initialize our message flags in session state
    if "tx_success" not in st.session_state:
        st.session_state.tx_success = False
    if "tx_error" not in st.session_state:
        st.session_state.tx_error = False

    # 3. Show messages if the flags were triggered by the callback
    if st.session_state.tx_success:
        st.success("✅ Transaction submitted! Analytics updated in real-time.")
        st.session_state.tx_success = False # Reset so it disappears on next action
        
    if st.session_state.tx_error:
        st.error("❌ Please select items first, or ensure the dataset exists.")
        st.session_state.tx_error = False

    # 4. Draw the widget (it connects to session_state.pos_basket automatically)
    st.multiselect("Customer buys:", AVAILABLE_ITEMS, key="pos_basket")
    
    # 5. Draw the button and link it to the callback using 'on_click'
    st.button("Submit Transaction", type="primary", on_click=process_transaction)
# --- TAB 3: ADMIN AI ---
with tab3:
    colA, colB = st.columns([0.8, 0.2])
    with colA:
        st.subheader("🤖 AI Data Strategist")
        st.write("Ask the AI to interpret the Apriori algorithms and suggest business strategies.")
    with colB:
        if st.button("🗑️ Clear Memory"):
            st.session_state.admin_messages = []
            st.rerun()

    if "admin_messages" not in st.session_state:
        st.session_state.admin_messages = [{"role": "assistant", "content": "Director, how can I assist with today's Market Basket metrics?"}]

    chat_container = st.container(height=400)
    with chat_container:
        for message in st.session_state.admin_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if user_question := st.chat_input("Ask about lift, support, or marketing strategies..."):
        if not st.session_state.groq_api_key:
            st.error("Please return to the Welcome page and enter the API Key.")
        else:
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(user_question)
            st.session_state.admin_messages.append({"role": "user", "content": user_question})

            system_prompt = f"""
            You are a Senior Data Scientist analyzing Market Basket Analysis (MBA) for the store owner.
            RAW DATA METRICS: {rules_text}
            INSTRUCTIONS:
            1. Analyze the user's request using the RAW DATA METRICS provided.
            2. Speak technically. Use terms like 'Lift', 'Confidence', 'Antecedents', and 'Apriori'.
            3. Explain exactly what the math means for their store layout or bundling strategy.
            4. If Lift is > 1, emphasize the strong relationship.
            """
            
            api_messages = [{"role": "system", "content": system_prompt}] + st.session_state.admin_messages

            with chat_container:
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    try:
                        url = "https://api.groq.com/openai/v1/chat/completions"
                        headers = {"Authorization": f"Bearer {st.session_state.groq_api_key}", "Content-Type": "application/json"}
                        payload = {"model": "llama-3.3-70b-versatile", "messages": api_messages}
                        response = requests.post(url, json=payload, headers=headers)
                        if response.status_code == 200:
                            bot_reply = response.json()['choices'][0]['message']['content']
                            message_placeholder.markdown(bot_reply)
                            st.session_state.admin_messages.append({"role": "assistant", "content": bot_reply})
                    except Exception as e:
                        st.error(f"Error: {e}")