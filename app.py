import streamlit as st
from langflow.load import run_flow_from_json
import os
import uuid

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AgentInvest Pro",
    page_icon="📊",
    layout="wide", # Switched to wide for a dashboard feel
    initial_sidebar_state="collapsed"
)

# --- 2. CUSTOM CSS FOR BEAUTIFICATION ---
st.markdown("""
    <style>
    /* Main container styling */
    .main {
        background-color: #f8f9fa;
    }
    /* Title styling */
    h1 {
        color: #0f172a;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
    }
    /* Subtitle styling */
    p {
        color: #475569;
        font-size: 1.1rem;
    }
    /* Button styling */
    .stButton>button {
        background-color: #2563eb;
        color: white;
        border-radius: 8px;
        font-weight: 600;
        border: none;
        padding: 0.5rem 2rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #1d4ed8;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    /* Input area styling */
    .stTextArea>div>div>textarea {
        border-radius: 10px;
        border: 1px solid #e2e8f0;
    }
    /* Result card styling */
    .result-card {
        background-color: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #2563eb;
        margin-top: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONFIGURATION & STATE ---
FLOW_FILENAME = "Basic trader.json"
CHAT_INPUT_ID = "ChatInput-Y5BqI"

if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())

# --- 4. HEADER SECTION ---
col1, col2 = st.columns([1, 5])
with col1:
    # You can replace this with a real logo image if you have one
    st.markdown("## 🛡️") 
with col2:
    st.title("AgentInvest Pro")
    st.markdown("#### Institutional-Grade AI Equity Research")

st.markdown("---")

# --- 5. CHECK FOR FILE ---
if not os.path.exists(FLOW_FILENAME):
    st.error(f"⚠️ Critical Error: Flow file '{FLOW_FILENAME}' not found.")
    st.stop()

# --- 6. MAIN INTERFACE ---
# We use columns to center the input form slightly for better focus
left_spacer, main_col, right_spacer = st.columns([1, 6, 1])

with main_col:
    with st.form("chat_form"):
        st.markdown("### 🎯 Start Your Analysis")
        user_input = st.text_area(
            "Enter Ticker or Strategy:", 
            placeholder="e.g., 'Analyze AAPL for a long-term portfolio and check recent regulatory news.'", 
            height=120,
            label_visibility="collapsed"
        )
        
        # Action Bar
        col_submit, col_clear = st.columns([1, 5])
        with col_submit:
            submitted = st.form_submit_button("🚀 Run Analysis")
        with col_clear:
            # Placeholder for layout alignment
            pass

# --- 7. EXECUTION LOGIC ---
if submitted and user_input:
    with main_col:
        # Progress indicator
        with st.status("🤖 Agent is working...", expanded=True) as status:
            st.write("🔄 Initializing session...")
            
            try:
                tweaks = {
                    CHAT_INPUT_ID: {
                        "input_value": user_input,
                        "session_id": st.session_state["session_id"]
                    }
                }

                st.write("🔍 Gathering market data & news...")
                results = run_flow_from_json(
                    flow=FLOW_FILENAME,
                    input_value=user_input,
                    tweaks=tweaks,
                    session_id=st.session_state["session_id"]
                )
                
                status.update(label="✅ Analysis Complete!", state="complete", expanded=False)

                # Parse Output
                response_text = None
                for output in results:
                    if hasattr(output, 'outputs'):
                        for component_output in output.outputs:
                            if hasattr(component_output, 'results') and "message" in component_output.results:
                                message_data = component_output.results["message"]
                                if hasattr(message_data, 'text'):
                                    response_text = message_data.text
                                elif isinstance(message_data, dict) and "text" in message_data:
                                    response_text = message_data["text"]

                # Display Logic
                if response_text:
                    st.markdown(f"""
                    <div class="result-card">
                        <h3>📊 Analyst Report</h3>
                        <p>{response_text}</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning("Analysis finished, but the agent returned no text. Check the raw logs below.")
                    with st.expander("Raw Output Log"):
                        st.write(results)

            except Exception as e:
                status.update(label="❌ Analysis Failed", state="error")
                st.error("An error occurred during execution.")
                with st.expander("Error Details"):
                    st.write(e)
                    if "No module named" in str(e):
                        st.info("Tip: Check your requirements.txt")

# --- 8. FOOTER ---
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #64748b; font-size: 0.8rem;'>
        <b>Disclaimer:</b> This tool provides AI-generated analysis based on technical indicators and public news.<br>
        It does not constitute financial advice. Always verify data independently before trading.
    </div>
    """, 
    unsafe_allow_html=True
)
