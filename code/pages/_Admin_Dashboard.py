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
    rules_text = "No strong rules found." # Default fallback
    
    # --- 🔍 LIVE DATA PREPROCESSING AUDIT UI ---
    st.markdown("### 🔍 Live Data Preprocessing Audit")
    st.caption("Proves to the panel that inputs are sanitized (duplicates removed) before hitting the FP-Growth Engine.")
    
    total_txs = len(encoded_data) if encoded_data is not None else 0
    col_metric, col_raw, col_clean = st.columns([0.2, 0.4, 0.4])
    
    with col_metric:
        st.metric(label="Total Transactions Analyzed", value=total_txs)
        
    with col_raw:
        with st.container(border=True):
            st.write("🔴 **Raw User Input**")
            if "demo_raw_cart" in st.session_state and st.session_state.demo_raw_cart:
                for item in st.session_state.demo_raw_cart:
                    st.write(f"- {item}")
                st.caption(f"Count: {len(st.session_state.demo_raw_cart)} items")
            else:
                st.caption("Waiting for next transaction...")
                
    with col_clean:
        with st.container(border=True):
            st.write("🟢 **Preprocessed (Sent to AI)**")
            if "demo_clean_cart" in st.session_state and st.session_state.demo_clean_cart:
                for item in st.session_state.demo_clean_cart:
                    st.write(f"- {item}")
                dropped = len(st.session_state.demo_raw_cart) - len(st.session_state.demo_clean_cart)
                st.caption(f"Count: {len(st.session_state.demo_clean_cart)} items ({dropped} duplicates dropped)")
            else:
                st.caption("Waiting for next transaction...")
    st.markdown("---")
    # -------------------------------------------

    if encoded_data is not None:
        freq_items, rules, applied_threshold = mine_patterns(encoded_data)
        st.info(f"Engine auto-adjusted Min Support to **{applied_threshold*100}%** based on dataset density.")
        
        if rules is not None and not rules.empty:
            display_rules = rules.copy()
            display_rules['antecedents'] = display_rules['antecedents'].apply(lambda x: ', '.join(list(x)))
            display_rules['consequents'] = display_rules['consequents'].apply(lambda x: ', '.join(list(x)))
            rules_text = display_rules[['antecedents', 'consequents', 'support', 'confidence', 'lift']].head(10).to_string()
            
            cA, cB = st.columns(2)
            with cA:
                st.write("**Confidence vs. Lift**")
                st.scatter_chart(display_rules[['confidence', 'lift']], x='confidence', y='lift')
            with cB:
                st.write("**Top Antecedents by Support**")
                bar_data = display_rules.groupby('antecedents')['support'].max().sort_values(ascending=False).head(5)
                st.bar_chart(bar_data)
        else:
            st.warning("No patterns detected in this dataset.")

    if not display_rules.empty:
        st.markdown("---")
        st.subheader("📋 Full Market Basket Rules Table")
        cols_to_drop = ['zhangs_metric', 'jaccard', 'certainty', 'kulczynski', 'BVS_Score']
        clean_rules = display_rules.drop(columns=cols_to_drop, errors='ignore')
        st.dataframe(
            clean_rules.style.highlight_max(subset=['lift'], axis=0, color='#1e3a8a'), 
            use_container_width=True, 
            height=400
        )

# --- TAB 2: POS SIMULATOR & LIVE DATA MANAGEMENT ---
with tab2:
    st.subheader("🛒 Point of Sale Simulator")
    st.write("Inject live transactions into the active dataset to force the engine to adapt.")
    
    def process_transaction():
        basket = st.session_state.pos_basket
        if len(basket) > 0 and os.path.exists(st.session_state.current_dataset):
            # PREPROCESSING: Deduplicate the POS input using set()
            clean_basket = list(set([item.strip() for item in basket if item.strip()]))
            
            # --- 🔍 LIVE AUDIT TRAIL CAPTURE ---
            st.session_state.demo_raw_cart = basket.copy()
            st.session_state.demo_clean_cart = clean_basket.copy()
            # -----------------------------------

            new_tx_id = f"POS_LIVE_{random.randint(1000, 9999)}"
            with open(st.session_state.current_dataset, 'a', newline='') as f:
                writer = csv.writer(f)
                for item in clean_basket:
                    writer.writerow([new_tx_id, item])
            
            st.session_state.pos_basket = [] 
            st.session_state.tx_success = True 
        else:
            st.session_state.tx_error = True

    if "tx_success" not in st.session_state: st.session_state.tx_success = False
    if "tx_error" not in st.session_state: st.session_state.tx_error = False

    if st.session_state.tx_success:
        st.success("✅ Transaction submitted! Analytics updated in real-time.")
        st.session_state.tx_success = False 
    if st.session_state.tx_error:
        st.error("❌ Please select items first, or ensure the dataset exists.")
        st.session_state.tx_error = False

    st.multiselect("Customer buys:", AVAILABLE_ITEMS, key="pos_basket")
    st.button("Submit Transaction", type="primary", on_click=process_transaction)

    st.markdown("---")
    st.subheader("📝 Live Data Management (Recalibrate AI Engine)")
    
    if os.path.exists(st.session_state.current_dataset):
        df_manage = pd.read_csv(st.session_state.current_dataset, names=["Transaction_ID", "Item"])
        if not df_manage.empty:
            grouped_df = df_manage.groupby("Transaction_ID")["Item"].apply(list).reset_index()
            recent_txs = grouped_df.tail(5).iloc[::-1] # Show last 5
            
            for index, row in recent_txs.iterrows():
                tx_id = row["Transaction_ID"]
                items = row["Item"]
                
                with st.expander(f"🧾 Order: {tx_id} ({len(items)} items)"):
                    if st.button("❌ Void Entire Order", key=f"void_{tx_id}", type="primary"):
                        df_manage = df_manage[df_manage["Transaction_ID"] != tx_id]
                        df_manage.to_csv(st.session_state.current_dataset, index=False, header=False)
                        st.rerun()
                        
                    st.write("Or remove specific items:")
                    for idx, item in enumerate(items):
                        col_item, col_del = st.columns([0.8, 0.2])
                        col_item.write(f"• {item}")
                        if col_del.button("🗑️ Remove", key=f"del_{tx_id}_{idx}"):
                            # Drop just this specific row
                            drop_idx = df_manage[(df_manage['Transaction_ID'] == tx_id) & (df_manage['Item'] == item)].index
                            if not drop_idx.empty:
                                df_manage = df_manage.drop(drop_idx[0]) # drop first occurrence
                                df_manage.to_csv(st.session_state.current_dataset, index=False, header=False)
                                st.rerun()

# --- TAB 3: ADMIN AI ---
with tab3:
    colA, colB = st.columns([0.8, 0.2])
    with colA: st.subheader("🤖 AI Data Strategist")
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
                with st.chat_message("user"): st.markdown(user_question)
            st.session_state.admin_messages.append({"role": "user", "content": user_question})

            # --- 🧠 PREPARE LIVE DATA FOR THE AI'S BRAIN ---
            # 1. Get Top Antecedents by Support (Formatting it as text)
            top_antecedents_text = "None calculated."
            if not display_rules.empty:
                top_ants_df = display_rules.groupby('antecedents')['support'].max().sort_values(ascending=False).head(5)
                top_antecedents_text = top_ants_df.to_string()
                
            # 2. Get Recent POS Transactions
            recent_tx_text = "No recent transactions found."
            if os.path.exists(st.session_state.current_dataset):
                try:
                    df_recent = pd.read_csv(st.session_state.current_dataset, names=["Transaction_ID", "Item"])
                    if not df_recent.empty:
                        recent_tx_text = df_recent.tail(10).to_string(index=False)
                except Exception:
                    pass

            # --- 🛑 THE STRICT SYSTEM PROMPT ---
            system_prompt = f"""
            You are the Senior Data Scientist embedded in the Admin Back-Office of the Nexus Gaming Store.
            You DO have direct access to the live POS simulator, databases, and analytics because the backend explicitly provides them to you below.
            
            --- LIVE SYSTEM METRICS ---
            Total Transactions Analyzed: {total_txs}
            
            Top Antecedents by Support:
            {top_antecedents_text}
            
            Full Market Basket Rules Table:
            {rules_text}
            
            Most Recent Raw Transactions (POS/Web):
            {recent_tx_text}
            ---------------------------
            
            STRICT BEHAVIORAL INSTRUCTIONS:
            1. NEVER say "I don't have the ability to access or analyze your current market basket data." You ARE analyzing it right now. The exact data you need is provided in the LIVE SYSTEM METRICS above.
            2. NEVER recommend external tools like IBM SPSS, Tableau, or Power BI. YOU are the built-in analytics tool for Nexus Gaming.
            3. If the user asks for total transactions, top antecedents, or rules, simply read the metrics provided above and format them into a professional, easy-to-read response.
            4. Speak technically. Explain the math. If Lift is > 1, emphasize the relationship.
            """
            
            try:
                url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {"Authorization": f"Bearer {st.session_state.groq_api_key}", "Content-Type": "application/json"}
                payload = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "system", "content": system_prompt}] + st.session_state.admin_messages}
                response = requests.post(url, json=payload, headers=headers)
                if response.status_code == 200:
                    bot_reply = response.json()['choices'][0]['message']['content']
                    st.session_state.admin_messages.append({"role": "assistant", "content": bot_reply})
                    st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")