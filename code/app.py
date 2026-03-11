import streamlit as st

st.set_page_config(page_title="Nexus Gaming Portal", layout="centered", page_icon="🎮")

# 1. Initialize global states & AUTO-LOAD API KEY
if "groq_api_key" not in st.session_state:
    try:
        # Automatically pull the key from your hidden .streamlit/secrets.toml file
        st.session_state.groq_api_key = st.secrets["GROQ_API_KEY"]
    except (FileNotFoundError, KeyError):
        st.session_state.groq_api_key = ""

if "current_dataset" not in st.session_state:
    st.session_state.current_dataset = "../data/dataset_A_regular.csv"
if "cart" not in st.session_state:
    st.session_state.cart = []

# 2. Initialize UI states so your selections persist when you leave the page
if "ui_iteration" not in st.session_state:
    st.session_state.ui_iteration = "Iteration 1: Regular Season"

st.title("🎮 Welcome to Nexus Gaming")
st.markdown("### Choose your portal from the sidebar to the left:")

col1, col2 = st.columns(2)
with col1:
    st.info("**🛍️ Customer Store**\n\nThe front-end e-commerce experience. Buy games, see AI Promo Bundles, and checkout.")
with col2:
    st.success("**💼 Admin Dashboard**\n\nThe back-end for store owners. View Live MBA Analytics and use the POS.")

st.markdown("---")
st.subheader("⚙️ Global System Controls")

# --- NEW: AI Status Indicator ---
if st.session_state.groq_api_key:
    st.success("🟢 **AI Data Strategist:** Securely Connected via Local Secrets")
else:
    st.error("🔴 **AI Data Strategist:** Disconnected. (API Key not found in .streamlit/secrets.toml)")
st.markdown("<br>", unsafe_allow_html=True)


st.markdown("#### 🔄 Select Store Season (Data Phase)")
st.write("Set your configuration below and click **Enter** to apply changes across the whole system.")

st.radio(
    "Changing this updates Promo Bundles and Analytics, but only after you click Enter:",
    ("Iteration 1: Regular Season", "Iteration 2: Holiday Rush", "Iteration 3: Esports Season"),
    key="ui_iteration"
)

# 4. The Enter Button Logic
if st.button("🚀 Enter & Apply Settings", type="primary"):
    # Save the Dataset to the global variable based on the radio selection
    if "Regular" in st.session_state.ui_iteration:
        st.session_state.current_dataset = "../data/dataset_A_regular.csv"
    elif "Holiday" in st.session_state.ui_iteration:
        st.session_state.current_dataset = "../data/dataset_B_holiday.csv" 
    else:
        st.session_state.current_dataset = "../data/dataset_C_esports.csv"
        
    st.success(f"✅ System Active! Configuration locked in.\n\nCurrently analyzing: `{st.session_state.current_dataset}`")
else:
    # Always show what the current active system state is
    st.info(f"Current active dataset: `{st.session_state.current_dataset}`")