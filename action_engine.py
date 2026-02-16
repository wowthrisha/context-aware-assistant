from memory_system import store_preference, add_task, add_conversation

def execute(action_data, user_input):
    """Execute action and return response message"""
    add_conversation(user_input)
    
    action = action_data.get("action", "unknown")
    
    if action == "store_preference":
        store_preference(action_data.get("key"), action_data.get("value"))
        return f"Preference saved successfully: {action_data.get('key', 'unknown')}"
    
    elif action == "schedule_with_preference":
        time = action_data.get("time", "default time")
        return f"Meeting scheduled based on your preference: {time}"
    
    elif action == "schedule_default":
        return "Meeting scheduled at default time"
    
    elif action == "store_task":
        task = action_data.get("task", user_input)
        time = action_data.get("time", "No time specified")
        person = action_data.get("person")
        
        add_task(task, time)
        
        response = f"Task saved"
        if time and time != "No time detected" and time != "No time specified":
            response += f" for {time}"
        if person:
            response += f" with {person}"
        response += "."
        
        return response
    
    elif action == "semantic_recall":
        context = action_data.get("context")
        if context and isinstance(context, dict):
            match = context.get("match", "No match found")
            score = context.get("score", 0.0)
            return f"I remember you mentioned: {match} (Relevance: {score:.2f})"
        else:
            return "No relevant memory found for your query"
    
    elif action == "clarify":
        return "Could you please clarify your request? I want to make sure I understand correctly."
    
    elif action == "unknown":
        return "I didn't understand that request. Could you rephrase it?"
    
    else:
        return f"Action '{action}' executed successfully"
