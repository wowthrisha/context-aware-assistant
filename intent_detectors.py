"""
Multiple transformer-based intent detection implementations:
1. HuggingFace Zero-Shot Classification (facebook/bart-large-mnli)
2. Sentence Transformers with Semantic Similarity
3. Claude API (OpenAI-compatible)
"""

import os
import json
from typing import Tuple, Dict, Optional

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, use environment variables only

# Intent configuration
INTENT_CONFIG = {
    "set_preference": {"template": "User is setting their preference or configuration"},
    "set_reminder": {"template": "User is setting a reminder or alarm"},
    "schedule_meeting": {"template": "User is scheduling a meeting or appointment"},
    "retrieve_task": {"template": "User is retrieving or asking about stored information"},
    "create_task": {"template": "User is creating a new task or to-do item"},
    "unknown": {"template": "User intent is unclear or unknown"}
}

INTENT_EXAMPLES = {
    "set_preference": ["I prefer coffee over tea", "Set my timezone to EST", "I like quiet hours from 9-5"],
    "set_reminder": ["Remind me about the meeting", "Alert me in 30 minutes", "Set an alarm for 6 AM"],
    "schedule_meeting": ["Schedule a meeting for tomorrow", "Book an appointment with John", "Arrange a call next week"],
    "retrieve_task": ["What did I say earlier", "Did I mention anything about the project", "Do you remember my preferences"],
    "create_task": ["Submit the report by Friday", "Call the client", "Prepare the presentation", "Send an email"],
}

# ============= 1. HuggingFace Zero-Shot Classification =============

def init_huggingface_classifier():
    """Initialize HuggingFace zero-shot classifier"""
    try:
        from transformers import pipeline
        classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
            device=-1  # CPU
        )
        return classifier
    except Exception as e:
        print(f"[ERROR] Failed to initialize HuggingFace classifier: {e}")
        return None

def detect_intent_huggingface(text: str, classifier=None) -> Tuple[str, float]:
    """Detect intent using HuggingFace zero-shot classification"""
    if classifier is None:
        classifier = init_huggingface_classifier()
    
    if classifier is None:
        return "unknown", 0.3
    
    try:
        intent_labels = list(INTENT_CONFIG.keys())
        templates = [INTENT_CONFIG[label]["template"] for label in intent_labels]
        
        # Classify with templates
        result = classifier(
            text,
            templates,
            multi_class=False
        )
        
        # Map back to intent
        template_to_intent = {
            INTENT_CONFIG[label]["template"]: label for label in intent_labels
        }
        
        matched_intent = template_to_intent.get(result["labels"][0], "unknown")
        confidence = float(result["scores"][0])
        
        return matched_intent, confidence
    except Exception as e:
        print(f"[ERROR] HuggingFace inference failed: {e}")
        return "unknown", 0.3

# ============= 2. Sentence Transformers with Semantic Similarity =============

def init_sentence_transformer():
    """Initialize Sentence Transformers for semantic similarity"""
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2")
        return model
    except Exception as e:
        print(f"[ERROR] Failed to initialize Sentence Transformers: {e}")
        return None

def detect_intent_sentence_transformers(text: str, model=None) -> Tuple[str, float]:
    """Detect intent using Sentence Transformers semantic similarity"""
    if model is None:
        model = init_sentence_transformer()
    
    if model is None:
        return "unknown", 0.3
    
    try:
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np
        
        # Encode user input
        user_embedding = model.encode(text, convert_to_tensor=False)
        
        # Compute similarity to intent examples
        best_intent = "unknown"
        best_score = 0.3
        
        for intent, examples in INTENT_EXAMPLES.items():
            for example in examples:
                example_embedding = model.encode(example, convert_to_tensor=False)
                similarity = cosine_similarity(
                    [user_embedding],
                    [example_embedding]
                )[0][0]
                
                if similarity > best_score:
                    best_score = similarity
                    best_intent = intent
        
        return best_intent, float(best_score)
    except Exception as e:
        print(f"[ERROR] Sentence Transformers inference failed: {e}")
        return "unknown", 0.3

# ============= 3. Claude API (via OpenAI-compatible interface) =============

def detect_intent_claude(text: str, api_key: Optional[str] = None) -> Tuple[str, float]:
    """Detect intent using Claude API"""
    api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        print("[WARNING] ANTHROPIC_API_KEY not set. Skipping Claude detection.")
        return "unknown", 0.3
    
    try:
        import anthropic
        
        client = anthropic.Anthropic(api_key=api_key)
        
        intent_list = ", ".join(INTENT_CONFIG.keys())
        
        prompt = f"""Analyze the user's intent from the following message and classify it into one of these categories: {intent_list}

User message: "{text}"

Respond with ONLY a JSON object in this format:
{{"intent": "<intent>", "confidence": <0.0-1.0>}}

Where confidence is how certain you are (1.0 = very certain, 0.0 = not certain).
Available intents: {intent_list}"""
        
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=100,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = message.content[0].text.strip()
        result = json.loads(response_text)
        
        intent = result.get("intent", "unknown")
        confidence = float(result.get("confidence", 0.3))
        
        # Validate intent
        if intent not in INTENT_CONFIG:
            intent = "unknown"
            confidence = 0.3
        
        return intent, confidence
    except Exception as e:
        print(f"[ERROR] Claude API inference failed: {e}")
        return "unknown", 0.3

# ============= Unified Interface =============

class TransformerIntentDetector:
    """Unified intent detector with multiple backends"""
    
    def __init__(self, backend: str = "huggingface", api_key: Optional[str] = None):
        """
        Initialize detector with specified backend
        
        Args:
            backend: One of "huggingface", "sentence_transformers", "claude"
            api_key: Optional API key for Claude (overrides environment variable)
        """
        self.backend = backend
        self.model = None
        self.classifier = None
        
        if backend == "huggingface":
            self.classifier = init_huggingface_classifier()
        elif backend == "sentence_transformers":
            self.model = init_sentence_transformer()
        elif backend == "claude":
            self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
    
    def detect(self, text: str) -> Tuple[str, float]:
        """Detect intent using configured backend"""
        if self.backend == "huggingface":
            return detect_intent_huggingface(text, self.classifier)
        elif self.backend == "sentence_transformers":
            return detect_intent_sentence_transformers(text, self.model)
        elif self.backend == "claude":
            return detect_intent_claude(text, self.api_key)
        else:
            return "unknown", 0.3
    
    def switch_backend(self, backend: str, api_key: Optional[str] = None) -> bool:
        """Switch to a different backend"""
        try:
            self.backend = backend
            if backend == "huggingface":
                self.classifier = init_huggingface_classifier()
            elif backend == "sentence_transformers":
                self.model = init_sentence_transformer()
            elif backend == "claude":
                self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to switch to {backend}: {e}")
            return False
