import re
from datetime import datetime
from typing import Optional

def analyze_input(user_input, intent_backend: Optional[str] = None, claude_api_key: Optional[str] = None):
    """Analyze user input with intent detection (rule-based or transformer-based)
    
    Args:
        user_input: The user's input text
        intent_backend: One of "Rule-Based", "Sentence Transformers", "HuggingFace", "Claude API"
                       If None or "Rule-Based", uses rule-based detection
    """
    
    entities = []
    time_entity = None
    person_entity = None

    # Extract time/date entities - MORE COMPREHENSIVE PATTERNS
    time_patterns = [
        r'\d{1,2}\s+(?:january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{4}',  # Most complete: 17 feb 2026
        r'\d{1,2}:\d{2}\s*(?:am|pm|AM|PM)',  # 10:30 am
        r'\d{1,2}\s+(?:am|pm|AM|PM)',  # 3 pm, 10 am (without colon)
        r'\d{1,2}/\d{1,2}/\d{2,4}',  # 02/16/2026
        r'(?:today|tomorrow|tonight|yesterday)',  # relative dates
        r'(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)',  # days
        r'\d{1,2}\s+(?:january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)',  # Fallback: 17 feb
    ]
    
    for pattern in time_patterns:
        matches = re.finditer(pattern, user_input, re.IGNORECASE)
        for match in matches:
            time_str = match.group()
            # Prefer the most complete date (with year) over partial dates
            if time_entity is None or (len(time_str) >= len(time_entity)):
                time_entity = time_str
                if not entities or entities[-1][1] != "TIME" or entities[-1][0] != time_str:
                    entities.append((time_str, "TIME"))
    
    # Extract person entities (names like "kavita mam", "john", "alice sir", etc.)
    # First try: Name + title pattern
    person_pattern_with_title = r'\b[A-Z][a-z]+(?:\s+(?:mam|sir|madam|mrs|mr|ms|dr|prof|dad|mom))\b'
    person_matches = re.finditer(person_pattern_with_title, user_input, re.IGNORECASE)
    for match in person_matches:
        name = match.group()
        person_entity = name
        entities.append((name, "PERSON"))
    
    # Second try: Names after prepositions (to, with, from, by, etc.) - lowercase names
    if not person_entity:
        preposition_pattern = r'(?:to|with|from|by|for)\s+([a-z]+)\b'
        prep_matches = re.finditer(preposition_pattern, user_input, re.IGNORECASE)
        for match in prep_matches:
            name = match.group(1)
            # Filter common words, time-related words, and day names
            excluded_words = {
                "the", "you", "me", "him", "her", "it", "them", "time", "submit",
                "morning", "afternoon", "evening", "night", "today", "tomorrow", "yesterday",
                "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
                "january", "february", "march", "april", "may", "june", "july", "august",
                "september", "october", "november", "december", "jan", "feb", "mar", "apr",
                "jun", "jul", "aug", "sep", "oct", "nov", "dec", "tonight", "date", "time",
                "day", "hour", "minute", "week", "month", "year", "pm", "am"
            }
            if name not in excluded_words and len(name) > 2:
                person_entity = name
                entities.append((name, "PERSON"))
                break
    
    # Third try: Just capitalized words (excluding common words)
    if not person_entity:
        person_pattern = r'\b[A-Z][a-z]+\b'
        person_matches = re.finditer(person_pattern, user_input)
        for match in person_matches:
            name = match.group()
            # Filter common words that shouldn't be names
            excluded_words = {
                "I", "The", "This", "That", "What", "When", "Where", "Why", "How", "You", "Submit",
                "Alert", "Remind", "Your", "Form", "Morning", "Afternoon", "Evening", "Night",
                "Today", "Tomorrow", "Yesterday", "Monday", "Tuesday", "Wednesday", "Thursday",
                "Friday", "Saturday", "Sunday", "January", "February", "March", "April", "June",
                "July", "August", "September", "October", "November", "December", "Jan", "Feb",
                "Mar", "Apr", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Tonight",
                "Date", "Time", "Day", "Hour", "Minute", "Week", "Month", "Year", "Pm", "Am"
            }
            if name not in excluded_words and len(name) > 2:
                person_entity = name
                entities.append((name, "PERSON"))
                break  # Take only first valid name

    # Use transformer-based or rule-based intent detection
    if intent_backend and intent_backend != "Rule-Based":
        # Map UI names to backend names
        backend_map = {
            "Sentence Transformers": "sentence_transformers",
            "HuggingFace": "huggingface",
            "Claude API": "claude"
        }
        backend = backend_map.get(intent_backend, "sentence_transformers")
        
        try:
            from intent_detectors import TransformerIntentDetector
            # Pass API key for Claude backend
            api_key = claude_api_key if backend == "claude" else None
            detector = TransformerIntentDetector(backend=backend, api_key=api_key)
            intent, confidence = detector.detect(user_input)
            
            # If transformer returns unknown with low confidence, might be an error
            if intent == "unknown" and confidence < 0.5:
                # Check if it's a missing dependency issue
                if backend == "claude" and not api_key:
                    raise ValueError("Claude API key required")
                # Otherwise fall back to rule-based
                intent, confidence = detect_intent_rule_based(user_input)
        except ImportError as e:
            # Missing dependencies - fall back gracefully
            import warnings
            warnings.warn(f"Transformer backend '{backend}' dependencies not installed: {e}. Install with: pip install transformers sentence-transformers anthropic")
            intent, confidence = detect_intent_rule_based(user_input)
        except Exception as e:
            # Other errors - fall back to rule-based
            import warnings
            warnings.warn(f"Transformer backend '{backend}' failed: {e}. Falling back to rule-based.")
            intent, confidence = detect_intent_rule_based(user_input)
    else:
        # Use rule-based intent detection (fast, reliable, no model downloads)
        intent, confidence = detect_intent_rule_based(user_input)

    return {
        "intent": intent,
        "entities": entities,
        "time": time_entity,
        "person": person_entity,
        "confidence": confidence
    }


def detect_intent_rule_based(text):
    """Fallback rule-based intent detection with priority ordering"""
    text = text.lower()

    # PRIORITY 1: Retrieval / memory recall - CHECK FIRST to avoid false positives
    # Patterns: "what have I", "did I mention", "do you remember", "what did I tell"
    if any(phrase in text for phrase in ["what have i", "what did", "did i mention", "do you remember", "what have you told", "tell me about"]):
        return "retrieve_task", 0.8
    if text.startswith("what") and any(word in text for word in ["told", "said", "mentioned", "earlier"]):
        return "retrieve_task", 0.8

    # PRIORITY 2: Preference (but NOT in retrieve contexts)
    if "prefer" in text and "remember" not in text:
        return "set_preference", 0.9

    # PRIORITY 3: Reminder / alert
    if any(word in text for word in ["remind", "reminder", "alert"]):
        return "set_reminder", 0.9

    # PRIORITY 4: Meeting scheduling (but NOT in generic contexts)
    if any(word in text for word in ["schedule", "meeting", "appoint"]):
        # Avoid false positive: "did I mention anything about the meeting" is retrieve, not schedule
        if "did i mention" not in text and "what" not in text:
            return "schedule_meeting", 0.9

    # PRIORITY 5: Generic task creation (submit, attend, complete, finish, send, call, pay)
    if any(word in text for word in [
        "submit", "attend", "complete", "finish",
        "send", "call", "pay", "buy", "prepare",
        "visit", "meet"
    ]):
        return "create_task", 0.85

    return "unknown", 0.3
