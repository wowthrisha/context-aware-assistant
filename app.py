import streamlit as st

# ===== SAFE IMPORT BLOCK =====
try:
    from nlp_engine import analyze_input
    from reasoning_engine import reason
    from action_engine import execute
    from memory_system import load_memory
except Exception as e:
    st.error(f"Import Error: {e}")
    st.stop()

st.set_page_config(page_title="NIXIN AI", layout="centered")

st.title("🧠 NIXIN AI - Context Aware Assistant")
st.markdown("Persistent Memory • Transformer Recall • Context Fusion")

user_input = st.text_input("Enter your command:")

if st.button("Run Assistant"):

    if user_input:

        intent_data = analyze_input(user_input)

        st.subheader("Intent Analysis")
        st.write("Intent:", intent_data["intent"])
        st.write("Confidence:", intent_data["confidence"])
        st.write("Entities:", intent_data["entities"])

        action_data = reason(intent_data, user_input)

        st.subheader("Assistant Response")

        import io
        import sys

        buffer = io.StringIO()
        sys.stdout = buffer
        execute(action_data, user_input)
        sys.stdout = sys.__stdout__

        st.success(buffer.getvalue())

st.subheader("Persistent Memory Snapshot")

try:
    memory = load_memory()
    st.json(memory)
except Exception as e:
    st.error(f"Memory Load Error: {e}")
