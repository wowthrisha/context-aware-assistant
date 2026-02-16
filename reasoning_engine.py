from memory_system import store_preference, add_task, get_preference
from vector_memory import semantic_search

CONFIDENCE_THRESHOLD = 0.75

def reason(intent_data, user_input):
    """Reason about intent and create action plan with reasoning"""
    
    confidence = intent_data.get("confidence", 0.0)
    
    if confidence < CONFIDENCE_THRESHOLD:
        return {
            "action": "clarify",
            "reasoning": f"Confidence level ({confidence:.1%}) is below threshold ({CONFIDENCE_THRESHOLD:.1%}). Need clarification."
        }
    
    intent = intent_data.get("intent", "unknown")
    time_entity = intent_data.get("time")
    person_entity = intent_data.get("person")
    
    if intent == "set_preference":
        return {
            "action": "store_preference",
            "key": "meeting_time",
            "value": user_input,
            "reasoning": "User is setting a preference. Storing preference for future use."
        }
    
    if intent == "schedule_meeting":
        pref = get_preference("meeting_time")
        if pref:
            return {
                "action": "schedule_with_preference",
                "time": pref,
                "reasoning": f"Found stored preference for meeting time: {pref}. Using preference."
            }
        else:
            return {
                "action": "schedule_default",
                "reasoning": "No stored preference found. Using default meeting time."
            }
    
    if intent == "set_reminder":
        reasoning_parts = ["User wants to set a reminder"]
        if time_entity:
            reasoning_parts.append(f"with time: {time_entity}")
        if person_entity:
            reasoning_parts.append(f"for person: {person_entity}")
        
        return {
            "action": "store_task",
            "task": user_input,
            "time": time_entity if time_entity else "No time detected",
            "person": person_entity,
            "reasoning": ". ".join(reasoning_parts) + "."
        }
    
    if intent == "retrieve_task":
        context = semantic_search(user_input)
        if context:
            return {
                "action": "semantic_recall",
                "context": context,
                "reasoning": f"Searching memory for similar past conversations. Found match with relevance score: {context.get('score', 0.0):.2f}"
            }
        else:
            return {
                "action": "semantic_recall",
                "context": None,
                "reasoning": "Searching memory but no relevant past conversations found."
            }
    
    if intent == "create_task":
        reasoning_parts = ["User wants to create a task"]
        if time_entity:
            reasoning_parts.append(f"due by {time_entity}")
        if person_entity:
            reasoning_parts.append(f"assigned to {person_entity}")
        
        return {
            "action": "store_task",
            "task": user_input,
            "time": time_entity if time_entity else "No time detected",
            "person": person_entity,
            "reasoning": ". ".join(reasoning_parts) + "."
        }
    
    return {
        "action": "unknown",
        "reasoning": "Intent not recognized. Unable to determine appropriate action."
    }
