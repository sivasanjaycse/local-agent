"""Tests for the NLU Preprocessor module."""

import sys
import os

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from nlu.preprocessor import NLUPreprocessor


nlu = NLUPreprocessor()


def test(label, raw_input, expected_substring=None):
    """Run a single NLU test case."""
    result = nlu.process(raw_input)
    normalized = result["normalized_text"]
    status = "✅" if (
        expected_substring is None
        or expected_substring.lower() in normalized.lower()
    ) else "❌"

    print(f"\n{status} {label}")
    print(f"   Input       : \"{raw_input}\"")
    print(f"   Cleaned     : \"{result['cleaned_text']}\"")
    print(f"   Normalized  : \"{normalized}\"")
    print(f"   Valid       : {result['is_valid']}")
    print(f"   Transforms  : {result['transformations']}")
    if expected_substring and status == "❌":
        print(f"   Expected    : \"{expected_substring}\"")


print("=" * 60)
print("  NLU Preprocessor Tests")
print("=" * 60)


# --- Filler word removal ---

test(
    "Filler words stripped",
    "Um, uh, like, open Chrome basically",
    "open Chrome",
)

test(
    "Multiple fillers",
    "Hmm, er, like literally open Notepad",
    "open Notepad",
)


# --- Leading filler removal ---

test(
    "Leading fillers stripped",
    "Well, so, okay, open Calculator",
    "open Calculator",
)

test(
    "Hey/Hi prefix stripped",
    "Hey, open VS Code",
    "open VS Code",
)


# --- Polite phrase removal ---

test(
    "Polite wrapper: can you please",
    "Can you please open Chrome",
    "open Chrome",
)

test(
    "Polite wrapper: I'd like to",
    "I'd like to search for Python tutorials",
    "search for Python tutorials",
)

test(
    "Polite wrapper: would you",
    "Would you open Notepad",
    "open Notepad",
)


# --- Multi-word filler phrases ---

test(
    "Phrase: you know",
    "You know, open Chrome",
    "open Chrome",
)

test(
    "Phrase: I mean",
    "I mean, open VS Code",
    "open VS Code",
)


# --- Disfluency correction ---

test(
    "Repeated word: open open Chrome",
    "open open Chrome",
    "open Chrome",
)

test(
    "False start: open Ch- Chrome",
    "open Ch- Chrome",
    "open Chrome",
)


# --- Semantic normalization: app synonyms ---

test(
    "Synonym: visual studio code → VS Code",
    "open visual studio code",
    "open VS Code",
)

test(
    "Synonym: vscode → VS Code",
    "open vscode",
    "open VS Code",
)

test(
    "Synonym: google chrome → Chrome",
    "open google chrome",
    "open Chrome",
)

test(
    "Synonym: calc → Calculator",
    "open calc",
    "open Calculator",
)


# --- Semantic normalization: action synonyms ---

test(
    "Synonym: launch → open",
    "launch Chrome",
    "open Chrome",
)

test(
    "Synonym: fire up → open",
    "fire up Notepad",
    "open Notepad",
)

test(
    "Synonym: look up → search",
    "look up Python tutorials",
    "search Python tutorials",
)

test(
    "Synonym: capture screen → take a screenshot",
    "capture screen",
    "take a screenshot",
)

test(
    "Synonym: make a folder → create a folder",
    "make a folder called Projects",
    "create a folder called Projects",
)


# --- Combined: noisy real-world voice input ---

test(
    "Full pipeline: noisy voice command",
    "Um, hey, like, could you please launch visual studio code basically",
    "open VS Code",
)

test(
    "Full pipeline: stuttered command",
    "Okay so uh fire fire up google chrome",
    "open Chrome",
)

test(
    "Full pipeline: polite search",
    "Well, I'd like to look up Python tutorials please",
    "search Python tutorials",
)


# --- Edge cases ---

test(
    "Empty string",
    "",
)

result = nlu.process("")
assert not result["is_valid"], "Empty input should be invalid"
print("   ✅ is_valid = False for empty string")

test(
    "Only fillers",
    "um uh like hmm",
)

result = nlu.process("um uh like hmm")
assert not result["is_valid"], "All-filler input should be invalid"
print("   ✅ is_valid = False for all-filler input")

test(
    "Clean input unchanged",
    "open Chrome",
    "open Chrome",
)


print("\n" + "=" * 60)
print("  All tests completed!")
print("=" * 60)
