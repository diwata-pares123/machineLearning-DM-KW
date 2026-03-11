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

st.title("💼 Executive MBA Dashboard")
st.caption(f"Currently Analyzing Data Phase: `{st.session_state.current_dataset.split('/')[-1]}`")

tab1, tab2, tab3 = st.tabs(["📊 Business Insights", "🛒 Live POS Simulator", "🤖 AI Data Strategist"])

# --- TAB 1: EXECUTIVE ANALYTICS ---
with tab1:
    encoded_data = load_and_encode(st.session_state.current_dataset)
    display_rules = pd.DataFrame()
    rules_text = "No strong rules found." 
    total_txs = len(encoded_data) if encoded_data is not None else 0

    if encoded_data is not None:
        freq_items, rules, applied_threshold = mine_patterns(encoded_data)
        
        # --- 1. KPI HEADLINES ---
        st.subheader("📈 Live Performance Snapshot")
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        
        total_rules = len(rules) if rules is not None else 0
        max_lift = rules['lift'].max() if (rules is not None and not rules.empty) else 0
        max_conf = rules['confidence'].max() if (rules is not None and not rules.empty) else 0
        
        kpi1.metric(label="Total Transactions", value=total_txs)
        kpi2.metric(label="Active Bundles Found", value=total_rules)
        kpi3.metric(label="Highest Synergy (Lift)", value=f"{max_lift:.2f}x" if max_lift else "N/A")
        kpi4.metric(label="Highest Predictability", value=f"{max_conf*100:.1f}%" if max_conf else "N/A")
        
        st.info(f"🧠 **AI Engine Note:** The system auto-adjusted the minimum support threshold to **{applied_threshold*100:.2f}%** based on current dataset density.")
        st.markdown("---")

        if rules is not None and not rules.empty:
            display_rules = rules.copy()
            display_rules['antecedents'] = display_rules['antecedents'].apply(lambda x: ', '.join(list(x)))
            display_rules['consequents'] = display_rules['consequents'].apply(lambda x: ', '.join(list(x)))
            rules_text = display_rules[['antecedents', 'consequents', 'support', 'confidence', 'lift', 'leverage', 'conviction']].head(10).to_string()
            
            # --- 2. ACTIONABLE INSIGHTS (Put at the top for executives) ---
            st.subheader("💡 Strategic Directives")
            col_promo, col_trap = st.columns(2)
            
            with col_promo:
                best_rule = display_rules.iloc[0] 
                with st.container(border=True):
                    st.success(f"**⚡ Recommended Action:** {best_rule.get('Business_Action', 'Highlight these items together.')}")
                    st.write(f"**If they buy:** `{best_rule['antecedents']}`")
                    st.write(f"**Immediately recommend:** `{best_rule['consequents']}`")
                    st.caption(f"Sales Probability: {best_rule['confidence']*100:.0f}% | Bundle Multiplier: {best_rule['lift']:.2f}x")

            with col_trap:
                worst_rule = display_rules.sort_values(by=['lift'], ascending=True).iloc[0] 
                with st.container(border=True):
                    st.error("**⚠️ Budget Waste Warning:** Avoid running ads for this combo.")
                    st.write(f"**Items:** `{worst_rule['antecedents']}` + `{worst_rule['consequents']}`")
                    st.write("**Reason:** These items are bought together mostly by coincidence. Promoting them together will not increase overall sales.")
                    st.caption(f"Bundle Multiplier: {worst_rule['lift']:.2f}x (Near or below 1.0 means no true synergy)")

            st.markdown("---")
            
            # --- 3. VISUALIZATIONS ---
            st.subheader("📊 Purchase Behavior Visualized")
            cA, cB = st.columns(2)
            
            with cA:
                st.write("**Synergy vs. Predictability**")
                st.scatter_chart(display_rules[['confidence', 'lift']], x='confidence', y='lift', color="#1e3a8a")
                st.caption("🔍 **How to read:** Dots higher up (High Lift) are the strongest synergies. Dots further to the right (High Confidence) are the most guaranteed sales.")
                
            with cB:
                st.write("**Most Popular 'Trigger' Items**")
                bar_data = display_rules.groupby('antecedents')['support'].max().sort_values(ascending=False).head(5)
                st.bar_chart(bar_data, color="#10b981")
                st.caption("🔍 **How to read:** These are the items that most frequently start a multi-item purchase. Put these on the homepage.")
                
            # --- 4. FORMATTED DATA TABLE ---
            st.markdown("---")
            st.subheader("📋 Detailed Rules Matrix")
            st.caption("Sorted by strongest synergy. Values are formatted for easy reading.")
            
            clean_rules = display_rules[['antecedents', 'consequents', 'support', 'confidence', 'lift', 'leverage', 'conviction']].copy()
            clean_rules = clean_rules.rename(columns={'antecedents': 'If They Buy (X)', 'consequents': 'Recommend (Y)'})
            clean_rules = clean_rules.sort_values(by=['lift'], ascending=False)
            
            # Formats the table to show %, x, and limits decimals
            styled_df = clean_rules.style.format({
                'support': '{:.2%}',
                'confidence': '{:.2%}',
                'lift': '{:.2f}x',
                'leverage': '{:.4f}',
                'conviction': '{:.2f}'
            }).highlight_max(subset=['lift'], axis=0, color='#1e3a8a')
            
            st.dataframe(styled_df, use_container_width=True, height=300)

        else:
            st.warning("No patterns detected in this dataset yet. Run more transactions.")

    # --- 5. THE AUDIT EXPANDER (Hidden from main view but accessible) ---
    with st.expander("🛠️ Developer Audit: Data Preprocessing Logs"):
        col_raw, col_clean = st.columns(2)
        with col_raw:
            st.write("🔴 **Raw User Input**")
            if "demo_raw_cart" in st.session_state and st.session_state.demo_raw_cart:
                for item in st.session_state.demo_raw_cart:
                    st.write(f"- {item}")
            else:
                st.caption("Waiting for next transaction...")
                
        with col_clean:
            st.write("🟢 **Cleaned Output (Duplicates Dropped)**")
            if "demo_clean_cart" in st.session_state and st.session_state.demo_clean_cart:
                for item in st.session_state.demo_clean_cart:
                    st.write(f"- {item}")
            else:
                st.caption("Waiting for next transaction...")

# --- TAB 2: POS SIMULATOR & LIVE DATA MANAGEMENT ---
with tab2:
    st.subheader("🛒 Point of Sale Simulator")
    st.write("Inject live transactions into the active dataset to force the engine to adapt.")
    
    def process_transaction():
        basket = st.session_state.pos_basket
        if len(basket) > 0 and os.path.exists(st.session_state.current_dataset):
            clean_basket = list(set([item.strip() for item in basket if item.strip()]))
            st.session_state.demo_raw_cart = basket.copy()
            st.session_state.demo_clean_cart = clean_basket.copy()

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
            recent_txs = grouped_df.tail(5).iloc[::-1] 
            
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
                            drop_idx = df_manage[(df_manage['Transaction_ID'] == tx_id) & (df_manage['Item'] == item)].index
                            if not drop_idx.empty:
                                df_manage = df_manage.drop(drop_idx[0]) 
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

            top_antecedents_text = "None calculated."
            misleading_text = "None calculated." 
            if not display_rules.empty:
                top_ants_df = display_rules.groupby('antecedents')['support'].max().sort_values(ascending=False).head(5)
                top_antecedents_text = top_ants_df.to_string()
                
                misleading_df = display_rules.sort_values(by=['lift'], ascending=True).head(4)
                misleading_text = misleading_df[['antecedents', 'consequents', 'confidence', 'lift']].to_string()
                
            recent_tx_text = "No recent transactions found."
            if os.path.exists(st.session_state.current_dataset):
                try:
                    df_recent = pd.read_csv(st.session_state.current_dataset, names=["Transaction_ID", "Item"])
                    if not df_recent.empty:
                        recent_tx_text = df_recent.tail(10).to_string(index=False)
                except Exception:
                    pass

            system_prompt = f"""
            You are the Senior Data Scientist embedded in the Admin Back-Office of the Nexus Gaming Store.
            You DO have direct access to the live POS simulator, databases, and analytics because the backend explicitly provides them to you below.
            
            --- LIVE SYSTEM METRICS ---
            Total Transactions Analyzed: {total_txs}
            
            Top Antecedents by Support:
            {top_antecedents_text}
            
            Top Strongest Market Basket Rules (X = Antecedent, Y = Consequent):
            {rules_text}
            
            Potentially Misleading Rules (Lowest Lift):
            {misleading_text}
            
            Most Recent Raw Transactions (POS/Web):
            {recent_tx_text}
            ---------------------------
            
            STRICT BEHAVIORAL INSTRUCTIONS:
            1. NEVER say "I don't have the ability to access or analyze your current market basket data." You ARE analyzing it right now.
            2. NEVER recommend external tools. YOU are the built-in analytics tool for Nexus Gaming.
            3. Speak technically and use the data provided.
            4. UNDERSTAND LEVERAGE & CONVICTION:
               - Leverage: Support(A and C) - (Support(A) * Support(C)).
               - Conviction: (1 - Support(C)) / (1 - Confidence(A -> C)).
            5. EXPLAINING MISLEADING ITEMSETS: If asked about "misleading" itemsets, look at the "Potentially Misleading Rules (Lowest Lift)" section. Explain that even if Confidence is somewhat high, a Lift near or below 1.0 means the items are bought together mostly by coincidence. Tell the Director that creating a bundle or promo for these specific items would be a waste of marketing budget because buying item X does not actively drive the purchase of item Y.
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