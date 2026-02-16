"""
NIXIN AI - Layer 1 Context Engine
Streamlit Web Interface
"""

import streamlit as st
import json
import os
from datetime import datetime
from nlp_engine import analyze_input
from reasoning_engine import reason
from action_engine import execute

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, use environment variables only

# Page configuration
st.set_page_config(
    page_title="NIXIN AI - Context Engine",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set Streamlit dark theme
st.markdown("""
<style>
    /* Use Streamlit's native dark theme - minimal custom styling */
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)

# Use Streamlit's native dark theme - minimal custom styling
st.markdown("""
<style>
    /* Intent Badges - Clean professional styling */
    .intent-badge {
        display: inline-block;
        padding: 0.5em 1em;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.95em;
        margin: 0.5em 0;
    }
    
    .intent-schedule {
        background-color: #A23B72;
        color: white;
    }
    
    .intent-reminder {
        background-color: #F18F01;
        color: white;
    }
    
    .intent-preference {
        background-color: #C73E1D;
        color: white;
    }
    
    .intent-retrieve {
        background-color: #6A994E;
        color: white;
    }
    
    .intent-create {
        background-color: #2E86AB;
        color: white;
    }
    
    .intent-unknown {
        background-color: #757575;
        color: white;
    }
    
    /* Entity Tags */
    .entity-tag {
        display: inline-block;
        background-color: rgba(46, 134, 171, 0.2);
        padding: 0.3em 0.6em;
        border-radius: 4px;
        margin: 0.2em;
        font-size: 0.9em;
        border-left: 3px solid #2E86AB;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div style="text-align: center; font-size: 2.5em; font-weight: 600; margin-bottom: 0.5em;">🤖 NIXIN AI - Context Engine</div>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.1em; margin-bottom: 2em; opacity: 0.8;">Intelligent Intent Detection & Task Management</p>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    st.subheader("Intent Detection")
    intent_backend = st.selectbox(
        "Detection Method",
        ["Rule-Based", "Sentence Transformers", "HuggingFace", "Claude API"]
    )
    
    # Claude API Key Input (only show if Claude is selected)
    claude_api_key = None
    if intent_backend == "Claude API":
        st.subheader("🔑 Claude API Configuration")
        st.info("Enter your Claude API key below or set ANTHROPIC_API_KEY in .env file")
        
        # Try to load from environment first
        env_api_key = os.getenv("ANTHROPIC_API_KEY")
        
        if env_api_key:
            st.success("✅ API key loaded from .env file")
            use_env_key = st.checkbox("Use API key from .env file", value=True)
            if use_env_key:
                claude_api_key = env_api_key
            else:
                claude_api_key = st.text_input(
                    "Claude API Key",
                    type="password",
                    help="Enter your Anthropic Claude API key",
                    placeholder="sk-ant-..."
                )
        else:
            claude_api_key = st.text_input(
                "Claude API Key",
                type="password",
                help="Enter your Anthropic Claude API key",
                placeholder="sk-ant-..."
            )
        
        if not claude_api_key:
            st.warning("⚠️ Claude API key required for Claude API backend")
    
    st.subheader("Memory")
    if st.button("📋 Load Memory"):
        try:
            with open("memory.json", "r") as f:
                memory = json.load(f)
                st.success("Memory loaded!")
                st.json(memory)
        except FileNotFoundError:
            st.warning("No memory file found")
    
    st.subheader("🎤 Presentation Mode")
    presentation_mode = st.checkbox("Enable Presentation Mode", value=False, help="Shows comparison across all modes")
    
    st.subheader("Help")
    st.info("""
    **High-confidence test cases (one per mode):**
    - **Rule-Based:** "remind me to pay electricity bill on 20 feb 2026 at 7 pm"
    - **Sentence Transformers:** "please remind me about the project deadline tomorrow morning"
    - **HuggingFace:** "organise a team meeting with alice and bob next monday at 3 pm"
    - **Claude API:** "next friday after lunch, remind me to submit the final report to kavita mam"
    """)

# Main Content
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("💬 Input Your Request")
    user_input = st.text_input(
        "You:",
        placeholder="e.g., Schedule a meeting tomorrow at 3pm",
        label_visibility="collapsed"
    )

with col2:
    st.subheader("Analysis Mode")
    analysis_mode = st.toggle("Show Detailed Analysis", value=True)

if user_input:
    st.markdown("---")
    
    # Validate Claude API key if needed
    if intent_backend == "Claude API" and not claude_api_key:
        st.error("❌ Please provide a Claude API key to use Claude API backend")
        st.info("💡 You can set it in `.env` file or enter it in the sidebar above")
        st.stop()
    
    # Check for missing dependencies
    if intent_backend == "Sentence Transformers":
        try:
            import sentence_transformers
        except ImportError:
            st.error("❌ Sentence Transformers not installed")
            st.code("pip install sentence-transformers torch", language="bash")
            st.stop()
    
    if intent_backend == "HuggingFace":
        try:
            import transformers
        except ImportError:
            st.error("❌ Transformers not installed")
            st.code("pip install transformers torch", language="bash")
            st.stop()
    
    if intent_backend == "Claude API":
        try:
            import anthropic
        except ImportError:
            st.error("❌ Anthropic SDK not installed")
            st.code("pip install anthropic", language="bash")
            st.stop()
    
    # Analyze input with selected backend
    with st.spinner(f"Analyzing with {intent_backend}..."):
        try:
            intent_data = analyze_input(user_input, intent_backend=intent_backend, claude_api_key=claude_api_key)
        except Exception as e:
            st.error(f"❌ Error analyzing input: {str(e)}")
            st.info("💡 Falling back to Rule-Based detection...")
            intent_data = analyze_input(user_input, intent_backend="Rule-Based")
    
    # Display Results
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Intent Detected", intent_data["intent"], delta=None)
    
    with col2:
        confidence_pct = f"{int(intent_data['confidence'] * 100)}%"
        st.metric("Confidence", confidence_pct, delta=None)
    
    with col3:
        entity_count = len(intent_data["entities"])
        st.metric("Entities Found", entity_count, delta=None)
    
    st.markdown("---")
    
    # Intent Badge
    intent = intent_data["intent"]
    intent_class_map = {
        "schedule_meeting": "intent-schedule",
        "set_reminder": "intent-reminder",
        "set_preference": "intent-preference",
        "retrieve_task": "intent-retrieve",
        "create_task": "intent-create",
        "unknown": "intent-unknown"
    }
    
    intent_class = intent_class_map.get(intent, "intent-unknown")
    st.markdown(
        f'<div class="intent-badge {intent_class}">{intent.upper().replace("_", " ")}</div>',
        unsafe_allow_html=True
    )
    
    # Confidence Bar
    st.markdown('<div class="confidence-bar">', unsafe_allow_html=True)
    st.progress(float(intent_data["confidence"]))
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Detailed Analysis
    if analysis_mode:
        st.subheader("📊 Detailed Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Time Entity:**")
            st.code(str(intent_data["time"]) if intent_data["time"] else "None")
        
        with col2:
            st.write("**Person Entity:**")
            st.code(str(intent_data["person"]) if intent_data["person"] else "None")
        
        st.write("**All Entities:**")
        if intent_data["entities"]:
            entity_cols = st.columns(min(len(intent_data["entities"]), 3))
            for idx, (entity_text, entity_type) in enumerate(intent_data["entities"]):
                with entity_cols[idx % 3]:
                    st.markdown(f'<div class="entity-tag"><strong>{entity_type}:</strong> {entity_text}</div>', unsafe_allow_html=True)
        else:
            st.caption("No entities found")
    
    st.markdown("---")
    
    # Reasoning Engine
    st.subheader("🧠 Reasoning")
    action_data = reason(intent_data, user_input)
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Action Type:**")
        st.code(action_data.get("action", "Unknown"))
    
    with col2:
        st.write("**Reasoning:**")
        st.code(action_data.get("reasoning", "No reasoning available"))
    
    st.markdown("---")
    
    # Action Execution
    st.subheader("⚡ Response")
    response = execute(action_data, user_input)
    
    if response:
        st.success("✅ Action executed successfully")
        st.info(f"**Response:** {response}")
    else:
        st.warning("⚠️ Action executed but no response returned")
    
    # Presentation Mode: Compare All Modes
    if presentation_mode:
        st.markdown("---")
        st.subheader("🔍 Comparison: All 4 Modes")
        st.info("Comparing the same input across all detection methods")
        
        comparison_results = {}
        modes_to_test = ["Rule-Based", "Sentence Transformers", "HuggingFace", "Claude API"]
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, mode in enumerate(modes_to_test):
            status_text.text(f"Testing {mode}... ({idx+1}/{len(modes_to_test)})")
            progress_bar.progress((idx + 1) / len(modes_to_test))
            
            try:
                # Get Claude API key from .env if not already set
                claude_key_for_presentation = claude_api_key or os.getenv("ANTHROPIC_API_KEY")
                
                # Skip Claude if no API key
                if mode == "Claude API" and not claude_key_for_presentation:
                    comparison_results[mode] = {
                        "intent": "N/A",
                        "confidence": 0.0,
                        "status": "⚠️ API key required"
                    }
                else:
                    api_key = claude_key_for_presentation if mode == "Claude API" else None
                    result = analyze_input(user_input, intent_backend=mode, claude_api_key=api_key)
                    comparison_results[mode] = {
                        "intent": result["intent"],
                        "confidence": result["confidence"],
                        "status": "✅"
                    }
            except Exception as e:
                comparison_results[mode] = {
                    "intent": "Error",
                    "confidence": 0.0,
                    "status": f"❌ {str(e)[:30]}"
                }
        
        status_text.empty()
        progress_bar.empty()
        
        # Display comparison table
        st.markdown("### Results Comparison")
        
        # Create professional comparison table
        for mode, result in comparison_results.items():
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                
                with col1:
                    st.write(f"**{mode}**")
                
                with col2:
                    if result['intent'] != "N/A" and result['intent'] != "Error":
                        st.code(result['intent'])
                    else:
                        st.caption(result['intent'])
                
                with col3:
                    if result['confidence'] > 0:
                        st.progress(result['confidence'])
                        st.caption(f"{result['confidence']:.1%}")
                    else:
                        st.caption(result['status'])
                
                with col4:
                    if result['status'] == '✅':
                        st.markdown("✅")
                    elif '⚠️' in result['status']:
                        st.markdown("⚠️")
                    else:
                        st.markdown("❌")
                
                st.markdown("---")
        
        # Summary
        st.markdown("---")
        st.markdown("### 📊 Summary")
        working_modes = [m for m, r in comparison_results.items() if r['status'] == '✅']
        st.success(f"✅ {len(working_modes)}/{len(modes_to_test)} modes working")
        
        if len(working_modes) > 1:
            # Show agreement
            intents = [comparison_results[m]['intent'] for m in working_modes]
            if len(set(intents)) == 1:
                st.info(f"🎯 All modes agree: **{intents[0]}**")
            else:
                unique_intents = ', '.join(set(intents))
                st.warning(f"⚠️ Modes disagree: {unique_intents}")
    
    # Metadata
    with st.expander("📋 Metadata"):
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "intent_data": intent_data,
            "action_data": action_data,
            "detection_method": intent_backend
        }
        st.json(metadata)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: gray; font-size: 0.85em; padding: 1em 0;">
    NIXIN AI - Layer 1 Context Engine | Powered by Transformers & Streamlit
    </div>
    """,
    unsafe_allow_html=True
)
