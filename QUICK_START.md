# 🚀 Quick Start - How to Run & Show

## Step 1: Install Dependencies

```bash
cd /Users/thrisha/ip_transformer/context-aware-assistant
pip install -r requirements.txt
```

---

## Step 2: Run the Web UI (Best for Demonstrations)

```bash
streamlit run app_streamlit.py
```

**What happens:**
- ✅ App starts on `http://localhost:8501`
- ✅ Browser opens automatically
- ✅ Shows beautiful web interface

---

## Step 3: Demonstrate All 4 Modes

### In the Streamlit UI:

1. **Select Detection Method** from dropdown (sidebar):
   - Rule-Based
   - Sentence Transformers
   - HuggingFace
   - Claude API

2. **Enter text** in the input field:
   - Example: `"schedule a meeting tomorrow at 3pm"`

3. **Click or press Enter** to analyze

4. **View results:**
   - Intent detected
   - Confidence score
   - Entities found (time, person)
   - Detailed analysis

### Enable Presentation Mode:
- ✅ Check **"Enable Presentation Mode"** in sidebar
- ✅ Enter any text
- ✅ See all 4 modes compared side-by-side!

---

## 🎤 Best Demo Flow (5 minutes)

### 1. Rule-Based (30 sec)
- Select "Rule-Based"
- Input: `"schedule a meeting tomorrow at 3pm"`
- Show: Fast, no dependencies

### 2. Sentence Transformers (1 min)
- Select "Sentence Transformers"
- Input: `"remind me about the project"`
- Show: Semantic understanding

### 3. HuggingFace (1 min)
- Select "HuggingFace"
- Input: `"I prefer coffee over tea"`
- Show: Zero-shot learning

### 4. Claude API (1.5 min)
- Select "Claude API"
- Point out: "✅ API key loaded from .env file"
- Input: `"what did I tell you earlier"`
- Show: Highest accuracy

### 5. Presentation Mode (1 min)
- Enable "Presentation Mode"
- Input: `"schedule a meeting tomorrow"`
- Show: All 4 modes side-by-side comparison

---

## 📋 Alternative Ways to Run

### Command Line Interface
```bash
python3 main.py
```
Then type natural language inputs.

### REST API Server
```bash
python3 app.py
```
API runs on `http://localhost:5000`

### Run Tests
```bash
python3 test_all_modes.py
```
Tests all 4 modes automatically.

---

## ✅ Quick Checklist

- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file has Claude API key (optional)
- [ ] Run: `streamlit run app_streamlit.py`
- [ ] Browser opens automatically
- [ ] Test each mode from dropdown
- [ ] Enable Presentation Mode for comparison

---

**Ready to demonstrate! 🎉**
