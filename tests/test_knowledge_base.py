"""Tests for the Knowledge Base (Module 8)."""

import sys
import os
import tempfile

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from knowledge.database import KnowledgeBase


def run_tests():
    # Use a temp file so tests don't pollute the real DB
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    try:
        kb = KnowledgeBase(db_path=db_path)

        # ---- Test 1: Log a workflow ----
        print("Test 1: log_workflow... ", end="")
        kb.log_workflow(
            intent="CODING",
            user_input="open vs code",
            normalized_input="open VS Code",
            workflow={"steps": [{"action": "OPEN_APPLICATION", "target": "VS Code"}]},
            confirmed=True,
            executed=True,
        )
        history = kb.get_recent_history(limit=1)
        assert len(history) == 1
        assert history[0]["intent"] == "CODING"
        assert history[0]["confirmed"] == 1
        assert history[0]["executed"] == 1
        print("✅")

        # ---- Test 2: Log a rejected workflow ----
        print("Test 2: log rejected workflow... ", end="")
        kb.log_workflow(
            intent="ENTERTAINMENT",
            user_input="open spotify",
            normalized_input="open spotify",
            workflow={"steps": [{"action": "OPEN_WEBSITE", "target": "Spotify"}]},
            confirmed=False,
            executed=False,
        )
        history = kb.get_recent_history(limit=5)
        assert len(history) == 2
        assert history[0]["confirmed"] == 0  # most recent = rejected
        print("✅")

        # ---- Test 3: App usage tracking ----
        print("Test 3: update_app_usage... ", end="")
        kb.update_app_usage("VS Code", "CODING")
        kb.update_app_usage("VS Code", "CODING")
        kb.update_app_usage("Chrome", "CODING")

        top_apps = kb.get_top_apps("CODING")
        assert len(top_apps) == 2
        assert top_apps[0]["application"] == "VS Code"
        assert top_apps[0]["use_count"] == 2
        assert top_apps[1]["application"] == "Chrome"
        assert top_apps[1]["use_count"] == 1
        print("✅")

        # ---- Test 4: Website usage tracking ----
        print("Test 4: update_website_usage... ", end="")
        kb.update_website_usage("GitHub", "https://github.com", "CODING")
        kb.update_website_usage("GitHub", "https://github.com", "CODING")
        kb.update_website_usage("GitHub", "https://github.com", "CODING")
        kb.update_website_usage("YouTube", "https://youtube.com", "RESEARCH")

        coding_sites = kb.get_top_websites("CODING")
        assert len(coding_sites) == 1
        assert coding_sites[0]["website_name"] == "GitHub"
        assert coding_sites[0]["use_count"] == 3

        research_sites = kb.get_top_websites("RESEARCH")
        assert len(research_sites) == 1
        assert research_sites[0]["website_name"] == "YouTube"
        print("✅")

        # ---- Test 5: Temporal preferences ----
        print("Test 5: update_temporal_preference... ", end="")
        kb.update_temporal_preference("CODING")
        kb.update_temporal_preference("CODING")
        kb.update_temporal_preference("MEETING")

        from datetime import datetime
        now = datetime.now()
        temporal = kb.get_temporal_intents(hour=now.hour, day=now.weekday())
        assert len(temporal) >= 1
        assert temporal[0]["intent"] == "CODING"
        assert temporal[0]["frequency"] == 2
        print("✅")

        # ---- Test 6: Workflow Acceptance Rate (WAR) ----
        print("Test 6: get_workflow_acceptance_rate... ", end="")
        war = kb.get_workflow_acceptance_rate()
        assert war["total"] == 2       # 2 logged workflows
        assert war["accepted"] == 1    # 1 confirmed
        assert war["rate"] == 0.5
        print("✅")

        # ---- Test 7: Execution Reliability (ER) ----
        print("Test 7: get_execution_reliability... ", end="")
        er = kb.get_execution_reliability()
        assert er["total_executed"] == 1    # 1 executed
        assert er["successful"] == 1        # no errors
        assert er["rate"] == 1.0
        print("✅")

        # ---- Test 8: Log a failed execution ----
        print("Test 8: log failed execution... ", end="")
        kb.log_workflow(
            intent="SYSTEM",
            user_input="take a screenshot",
            normalized_input="take a screenshot",
            workflow={"steps": [{"action": "SYSTEM_ACTION", "type": "screenshot"}]},
            confirmed=True,
            executed=True,
            error="Permission denied",
        )
        er = kb.get_execution_reliability()
        assert er["total_executed"] == 2
        assert er["successful"] == 1
        assert er["rate"] == 0.5
        print("✅")

        # ---- Test 9: Custom workflows ----
        print("Test 9: save/get custom_workflow... ", end="")
        kb.save_custom_workflow(
            name="morning_coding",
            intent="CODING",
            workflow={"steps": [
                {"action": "OPEN_APPLICATION", "target": "VS Code"},
                {"action": "OPEN_WEBSITE", "target": "GitHub", "url": "https://github.com"},
            ]},
        )
        custom = kb.get_custom_workflow("morning_coding")
        assert custom is not None
        assert custom["intent"] == "CODING"
        assert len(custom["workflow_json"]["steps"]) == 2

        # Non-existent returns None
        assert kb.get_custom_workflow("nonexistent") is None
        print("✅")

        # ---- Test 10: Empty DB metrics ----
        print("Test 10: empty DB edge cases... ", end="")
        empty_kb = KnowledgeBase(db_path=":memory:")
        assert empty_kb.get_workflow_acceptance_rate()["rate"] == 0.0
        assert empty_kb.get_execution_reliability()["rate"] == 0.0
        assert empty_kb.get_top_apps("CODING") == []
        assert empty_kb.get_top_websites("CODING") == []
        assert empty_kb.get_temporal_intents() == []
        assert empty_kb.get_recent_history() == []
        empty_kb.close()
        print("✅")

        kb.close()

        print(f"\n{'=' * 50}")
        print(f"  All Knowledge Base tests passed! ✅")
        print(f"{'=' * 50}")

    finally:
        os.unlink(db_path)


if __name__ == "__main__":
    run_tests()
