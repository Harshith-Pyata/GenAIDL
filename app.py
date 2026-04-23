import os
import json
import re
import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

st.set_page_config(page_title="Adaptive TextGrad IDS", page_icon="🛡️", layout="wide")

# ==========================================
# 0. DEPLOYMENT-SAFE API KEY HANDLING
# ==========================================
with st.sidebar:
    st.header("⚙️ Settings")
    
    groq_api_key = None
    
    # We wrap this in a try-except block so it doesn't crash your local machine
    # if you don't have a .streamlit/secrets.toml file setup!
    try:
        if "GROQ_API_KEY" in st.secrets:
            groq_api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        pass # Completely ignore the error and move on
        
    # If it didn't find a cloud key, it will ask the user to type one in
    if not groq_api_key:
        groq_api_key = st.text_input("Enter Groq API Key", type="password", help="Get this from console.groq.com")
        
    if not groq_api_key:
        st.warning("⚠️ Please enter a Groq API Key to enable detection.")
# ==========================================
# 1. SESSION STATE INITIALIZATION
# ==========================================
default_values = {
    "protocol_type": "tcp", 
    "service": "http", 
    "flag": "SF", 
    "duration": 0, 
    "src_bytes": 250, 
    "dst_bytes": 5000,
    "num_failed_logins": 0, 
    "serror_rate": 0.0
}

for k, v in default_values.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================
def textualize_row_full(input_dict):
    """Dynamically converts inputted features into a readable text log."""
    log_parts = []
    for key, value in input_dict.items():
        clean_key = key.replace('_', ' ').title()
        log_parts.append(f"{clean_key}: {value}")
    return ", ".join(log_parts)

def load_neptune_anomaly():
    """Simulates a classic DoS attack (High error rate, 0 bytes)."""
    st.session_state.protocol_type = "tcp"
    st.session_state.service = "private"
    st.session_state.flag = "S0"
    st.session_state.duration = 0
    st.session_state.src_bytes = 0
    st.session_state.dst_bytes = 0
    st.session_state.num_failed_logins = 0
    st.session_state.serror_rate = 1.0

def load_normal_traffic():
    """Simulates benign HTTP connection passing the AI's current safe rules."""
    st.session_state.protocol_type = "tcp"
    st.session_state.service = "http"
    st.session_state.flag = "SF"
    st.session_state.duration = 15     # > 1 second
    st.session_state.src_bytes = 250   # < 1000 bytes
    st.session_state.dst_bytes = 800   # < 1000 bytes
    st.session_state.num_failed_logins = 0
    st.session_state.serror_rate = 0.0

# ==========================================
# 3. STREAMLIT UI LAYOUT
# ==========================================
st.header("🔍 Test a Single Network Log")
st.write("Enter the 8 core network parameters below to simulate a live connection.")

btn_col1, btn_col2 = st.columns(2)
with btn_col1:
    st.button("🚨 Load Sample Anomaly (Neptune DoS)", on_click=load_neptune_anomaly, use_container_width=True)
with btn_col2:
    st.button("✅ Load Normal Traffic (HTTP Web)", on_click=load_normal_traffic, use_container_width=True)

with st.form("manual_log_input"):
    st.subheader("Network Log Parameters")
    input_data = {}
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        input_data['protocol_type'] = st.selectbox("Protocol Type", ["tcp", "udp", "icmp"], key="protocol_type")
        input_data['duration'] = st.number_input("Duration", min_value=0, key="duration")
        input_data['num_failed_logins'] = st.number_input("Failed Logins", min_value=0, key="num_failed_logins")
        
    with col2:
        input_data['service'] = st.text_input("Service", key="service")
        input_data['src_bytes'] = st.number_input("Src Bytes", min_value=0, key="src_bytes")
        input_data['serror_rate'] = st.number_input("Serror Rate", min_value=0.0, max_value=1.0, key="serror_rate")
        
    with col3:
        input_data['flag'] = st.text_input("Flag", key="flag")
        input_data['dst_bytes'] = st.number_input("Dst Bytes", min_value=0, key="dst_bytes")

    submitted = st.form_submit_button("Detect Anomaly", type="primary", use_container_width=True)

# ==========================================
# 4. EXECUTION LOGIC & SMART PARSER
# ==========================================
if submitted:
    if not groq_api_key:
        st.error("Stop! You must enter a Groq API Key in the sidebar before running a detection.")
        st.stop()
        
    with st.spinner("Analyzing network log..."):
        user_input_log = textualize_row_full(input_data)
        
        with st.expander("👀 View Generated Log Text", expanded=False):
            st.info(user_input_log)
        
        # Initialize LLM dynamically inside the button using the user's key
        llm = ChatGroq(api_key=groq_api_key, model="llama-3.1-8b-instant", temperature=0.0)
        
        detector_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an Intrusion Detection System. 
            Follow these guidelines to classify the log:
            {guidelines}
            
            First, think step-by-step about the network log and whether it violates the guidelines. 
            Write your reasoning out.
            Then, end your response with EXACTLY this format:
            FINAL PREDICTION: 1 (if anomaly) or 0 (if normal)."""),
            ("human", "Network Log:\n{log}")
        ])
        
        detector_chain = detector_prompt | llm | StrOutputParser()
        
        # Robust File Loading for Deployment
        json_path = os.path.join(os.getcwd(), "final_guideline.json")
        try:
            with open(json_path, "r") as f:
                best_guideline = json.load(f)["final_guideline"]
        except (FileNotFoundError, json.JSONDecodeError):
            st.warning("⚠️ Could not locate the optimized JSON file. Using fallback baseline rules.")
            # Fallback rules in case the file doesn't deploy properly
            best_guideline = "Flag any connection with Duration < 1, Serror Rate > 0.5, or Src Bytes > 1000 as Anomaly (1). Otherwise, Normal (0)."
                
        try:
            response = detector_chain.invoke({
                "guidelines": best_guideline,
                "log": user_input_log
            }).strip()
            
            with st.expander("🛠️ Debug: View Raw LLM Output", expanded=True):
                st.write(f"**Raw AI Response:**\n\n{response}")
            
            # Smart Regex Parser
            match = re.search(r'FINAL PREDICTION:\s*([01])', response)
            
            if match:
                prediction = match.group(1)
                if prediction == '1':
                    st.error("🚨 **ANOMALY DETECTED!** This traffic matches known attack patterns.")
                elif prediction == '0':
                    st.success("✅ **NORMAL TRAFFIC.** No threats detected.")
            else:
                st.warning("⚠️ **INCONCLUSIVE.** The model did not output a valid 1 or 0 prediction format.")
                
        except Exception as e:
            st.error(f"Prediction failed: {e}")