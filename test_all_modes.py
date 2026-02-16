#!/usr/bin/env python3
"""
Comprehensive test script to verify all 4 intent detection modes work correctly.
Run this after setting up your .env file and installing dependencies.
"""

import os
import sys
from typing import Dict, List, Tuple

# Try to load .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")
    print("   Continuing without .env support...\n")

# Test cases: (input_text, expected_intent)
TEST_CASES = [
    ("schedule a meeting tomorrow at 3pm", "schedule_meeting"),
    ("remind me about the project deadline", "set_reminder"),
    ("I prefer coffee over tea", "set_preference"),
    ("what did I tell you earlier", "retrieve_task"),
    ("send an email to john", "create_task"),
    ("set my timezone to EST", "set_preference"),
    ("alert me in 30 minutes", "set_reminder"),
    ("book an appointment with alice", "schedule_meeting"),
    ("did I mention anything about the presentation", "retrieve_task"),
    ("submit the report by Friday", "create_task"),
    ("hello there", "unknown"),
    ("call the client tomorrow", "create_task"),
]

def test_mode(mode_name: str, backend_name: str, claude_key: str = None) -> Dict:
    """Test a single mode with all test cases"""
    from nlp_engine import analyze_input
    
    results = {
        "mode": mode_name,
        "backend": backend_name,
        "total": len(TEST_CASES),
        "correct": 0,
        "passed": [],
        "failed": [],
        "errors": []
    }
    
    print(f"\n{'='*70}")
    print(f"Testing {mode_name.upper()}")
    print(f"{'='*70}\n")
    
    for i, (text, expected_intent) in enumerate(TEST_CASES, 1):
        try:
            # Use Claude API key if provided
            api_key = claude_key if backend_name == "Claude API" else None
            result = analyze_input(text, intent_backend=mode_name, claude_api_key=api_key)
            
            detected_intent = result["intent"]
            confidence = result["confidence"]
            is_correct = detected_intent == expected_intent
            
            status = "✅" if is_correct else "❌"
            if is_correct:
                results["correct"] += 1
                results["passed"].append((text, detected_intent, confidence))
            else:
                results["failed"].append((text, expected_intent, detected_intent, confidence))
            
            print(f"{status} [{i:2d}/{len(TEST_CASES)}] {detected_intent:20} ({confidence:.2%}) | {text[:50]}")
            if not is_correct:
                print(f"   Expected: {expected_intent}")
                
        except Exception as e:
            results["errors"].append((text, str(e)))
            print(f"❌ [{i:2d}/{len(TEST_CASES)}] ERROR: {text[:50]}")
            print(f"   {str(e)[:60]}")
    
    accuracy = results["correct"] / results["total"] * 100
    print(f"\n{'-'*70}")
    print(f"Accuracy: {accuracy:.1f}% ({results['correct']}/{results['total']})")
    
    return results

def main():
    print("="*70)
    print("COMPREHENSIVE TEST: All 4 Intent Detection Modes")
    print("="*70)
    
    # Get Claude API key from environment
    claude_key = os.getenv("ANTHROPIC_API_KEY")
    
    all_results = []
    
    # Test each mode
    modes = [
        ("Rule-Based", "Rule-Based", None),
        ("Sentence Transformers", "Sentence Transformers", None),
        ("HuggingFace", "HuggingFace", None),
        ("Claude API", "Claude API", claude_key),
    ]
    
    for mode_name, backend_name, api_key in modes:
        try:
            results = test_mode(mode_name, backend_name, api_key)
            all_results.append(results)
        except KeyboardInterrupt:
            print("\n\n⚠️  Test interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Failed to test {mode_name}: {e}")
            all_results.append({
                "mode": mode_name,
                "correct": 0,
                "total": len(TEST_CASES),
                "errors": [("Initialization", str(e))]
            })
    
    # Summary
    print("\n\n" + "="*70)
    print("SUMMARY - All Modes")
    print("="*70)
    print(f"\n{'Mode':<25} {'Accuracy':<15} {'Status':<15}")
    print("-"*70)
    
    for result in all_results:
        accuracy = (result["correct"] / result["total"] * 100) if result["total"] > 0 else 0
        status = "✅ PASS" if accuracy >= 80 else "⚠️  PARTIAL" if accuracy > 0 else "❌ FAIL"
        print(f"{result['mode']:<25} {accuracy:>6.1f}%{'':6} {status:<15}")
    
    # Detailed failures
    print("\n" + "="*70)
    print("DETAILED RESULTS")
    print("="*70)
    
    for result in all_results:
        if result.get("failed"):
            print(f"\n❌ {result['mode']} - Failed Cases:")
            for text, expected, detected, conf in result["failed"]:
                print(f"   Input: '{text[:40]}...'")
                print(f"   Expected: {expected}, Got: {detected} ({conf:.2%})")
        
        if result.get("errors"):
            print(f"\n⚠️  {result['mode']} - Errors:")
            for text, error in result["errors"]:
                print(f"   Input: '{text[:40]}...'")
                print(f"   Error: {error[:60]}")
    
    # Final verdict
    print("\n" + "="*70)
    all_passed = all(r.get("correct", 0) / r.get("total", 1) >= 0.8 for r in all_results if r.get("total", 0) > 0)
    
    if all_passed:
        print("✅ ALL MODES WORKING CORRECTLY!")
    else:
        print("⚠️  Some modes need attention. Check details above.")
    
    print("="*70)
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    for result in all_results:
        if result.get("correct", 0) / result.get("total", 1) < 0.8:
            mode = result["mode"]
            if mode == "Claude API" and not claude_key:
                print(f"   - {mode}: Set ANTHROPIC_API_KEY in .env file")
            elif mode in ["Sentence Transformers", "HuggingFace"]:
                print(f"   - {mode}: Install dependencies: pip install transformers sentence-transformers torch")
            else:
                print(f"   - {mode}: Check for errors above")

if __name__ == "__main__":
    main()
