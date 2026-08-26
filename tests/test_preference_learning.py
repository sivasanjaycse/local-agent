"""Tests for the Preference Learning Engine (Module 7)."""

import sys
import os

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from knowledge.database import KnowledgeBase
from learning.preference_engine import PreferenceLearningEngine


def run_tests():
    # In-memory DB for isolation
    kb = KnowledgeBase(db_path=":memory:")
    engine = PreferenceLearningEngine(kb)

    # ---- Helper data ----
    nlu_result = {
        "original_text": "open vs code",
        "cleaned_text": "open vs code",
        "normalized_text": "open VS Code",
        "is_valid": True,
        "transformations": ["semantic_normalization"],
    }

    intent_result = {
        "intent": "CODING",
        "entities": {
            "applications": ["VS Code"],
            "websites": [{"name": "GitHub", "url": "https://github.com"}],
            "query": "",
            "topic": "coding",
            "action": "open",
            "file_target": "",
        },
        "reasoning": "User wants to code",
    }

    workflow = {
        "workflow_id": "coding",
        "intent": "CODING",
        "steps": [
            {"action": "OPEN_APPLICATION", "target": "VS Code"},
            {"action": "OPEN_WEBSITE", "target": "GitHub", "url": "https://github.com"},
        ],
        "description": "Start coding session — VS Code, GitHub",
        "reasoning": "User wants to code",
    }

    # ---- Test 1: Record accepted+executed interaction ----
    print("Test 1: record accepted+executed... ", end="")
    engine.record_interaction(
        nlu_result, intent_result, workflow,
        confirmed=True, executed=True,
    )
    history = kb.get_recent_history(limit=1)
    assert len(history) == 1
    assert history[0]["confirmed"] == 1
    assert history[0]["executed"] == 1
    print("✅")

    # ---- Test 2: App usage updated for executed workflow ----
    print("Test 2: app usage updated... ", end="")
    apps = engine.get_recommended_apps("CODING")
    assert "VS Code" in apps
    print("✅")

    # ---- Test 3: Website usage updated for executed workflow ----
    print("Test 3: website usage updated... ", end="")
    sites = engine.get_recommended_websites("CODING")
    assert len(sites) >= 1
    assert sites[0]["name"] == "GitHub"
    assert sites[0]["url"] == "https://github.com"
    print("✅")

    # ---- Test 4: Temporal preference updated ----
    print("Test 4: temporal preference updated... ", end="")
    suggestion = engine.get_temporal_suggestion()
    assert suggestion == "CODING"
    print("✅")

    # ---- Test 5: Record rejected interaction ----
    print("Test 5: record rejected interaction... ", end="")
    engine.record_interaction(
        nlu_result, intent_result, workflow,
        confirmed=False, executed=False,
    )
    # Rejected workflows should NOT update app/website usage
    apps = engine.get_recommended_apps("CODING")
    # VS Code count should still be 1 (not 2)
    top = kb.get_top_apps("CODING")
    assert top[0]["use_count"] == 1
    print("✅")

    # ---- Test 6: Record multiple to build up history ----
    print("Test 6: acceptance trend... ", end="")
    # Add more interactions: 3 accepted, 1 rejected = 4+1 rejected earlier = 5 total
    for _ in range(3):
        engine.record_interaction(
            nlu_result, intent_result, workflow,
            confirmed=True, executed=True,
        )

    trend = engine.get_acceptance_trend(last_n=20)
    assert trend["total"] == 5
    assert trend["accepted"] == 4   # 1 original + 3 new accepted
    assert trend["rate"] == 0.8
    print("✅")

    # ---- Test 7: Empty intent has no recommendations ----
    print("Test 7: no data for unknown intent... ", end="")
    assert engine.get_recommended_apps("MEETING") == []
    assert engine.get_recommended_websites("MEETING") == []
    print("✅")

    # ---- Test 8: Failed execution records error ----
    print("Test 8: failed execution logged... ", end="")
    engine.record_interaction(
        nlu_result, intent_result, workflow,
        confirmed=True, executed=True, error="App not found",
    )
    er = kb.get_execution_reliability()
    # 4 successful + 1 failed = 5 executed, 4 successful
    assert er["total_executed"] == 5
    assert er["successful"] == 4
    print("✅")

    # ---- Test 9: Multiple intents, temporal picks dominant ----
    print("Test 9: temporal picks dominant intent... ", end="")
    meeting_intent = {
        "intent": "MEETING",
        "entities": {"applications": [], "websites": [], "query": "", "topic": "", "action": "", "file_target": ""},
        "reasoning": "meeting",
    }
    meeting_workflow = {"workflow_id": "meeting", "intent": "MEETING", "steps": [], "description": "meeting", "reasoning": ""}
    meeting_nlu = {"original_text": "meeting", "cleaned_text": "meeting", "normalized_text": "meeting", "is_valid": True, "transformations": []}

    engine.record_interaction(meeting_nlu, meeting_intent, meeting_workflow, confirmed=True, executed=True)

    # CODING has more temporal hits, should still be dominant
    suggestion = engine.get_temporal_suggestion()
    assert suggestion == "CODING"
    print("✅")

    kb.close()

    print(f"\n{'=' * 50}")
    print(f"  All Preference Learning tests passed! ✅")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    run_tests()
