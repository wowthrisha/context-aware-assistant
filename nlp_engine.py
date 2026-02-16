import spacy

nlp = spacy.load("en_core_web_sm")

def analyze_input(user_input):

    doc = nlp(user_input)

    entities = []
    time_entity = None
    person_entity = None

    for ent in doc.ents:
        entities.append((ent.text, ent.label_))

        if ent.label_ in ["TIME", "DATE"]:
            time_entity = ent.text

        if ent.label_ == "PERSON":
            person_entity = ent.text

    intent = detect_intent(user_input)

    # Dynamic confidence
    confidence = 0.9 if intent != "unknown" else 0.3

    return {
        "intent": intent,
        "entities": entities,
        "time": time_entity,
        "person": person_entity,
        "confidence": confidence
    }


def detect_intent(text):
    text = text.lower()

    # Preference
    if "prefer" in text:
        return "set_preference"

    # Reminder / alert
    if any(word in text for word in ["remind", "reminder", "alert"]):
        return "set_reminder"

    # Meeting scheduling
    if any(word in text for word in ["schedule", "meeting", "appoint"]):
        return "schedule_meeting"

    # Retrieval / memory recall
    if any(word in text for word in ["when", "what did", "did i", "remember"]):
        return "retrieve_task"

    # Generic task creation (submit, attend, complete, finish, send, call, pay)
    if any(word in text for word in [
        "submit", "attend", "complete", "finish",
        "send", "call", "pay", "buy", "prepare",
        "visit", "meet"
    ]):
        return "create_task"

    return "unknown"
