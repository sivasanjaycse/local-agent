"""Tests for the Performance Metrics Collector."""

import sys
import os

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from knowledge.database import KnowledgeBase
from metrics.collector import MetricsCollector


def run_tests():
    kb = KnowledgeBase(db_path=":memory:")
    mc = MetricsCollector(kb)

    # ---- Test 1: WER — perfect match ----
    print("Test 1: WER perfect match... ", end="")
    wer = mc.compute_wer("open vs code", "open vs code")
    assert wer == 0.0
    print("✅")

    # ---- Test 2: WER — one substitution ----
    print("Test 2: WER one substitution... ", end="")
    wer = mc.compute_wer("open vs code", "open bs code")
    assert abs(wer - 1 / 3) < 0.01  # 1 error / 3 words
    print("✅")

    # ---- Test 3: WER — completely wrong ----
    print("Test 3: WER completely wrong... ", end="")
    wer = mc.compute_wer("open chrome", "take a screenshot now")
    assert wer > 0.5
    print("✅")

    # ---- Test 4: WER — empty reference ----
    print("Test 4: WER empty reference... ", end="")
    wer = mc.compute_wer("", "some text")
    assert wer == 1.0
    wer = mc.compute_wer("", "")
    assert wer == 0.0
    print("✅")

    # ---- Test 5: Intent accuracy — perfect ----
    print("Test 5: Intent accuracy perfect... ", end="")
    result = mc.compute_intent_accuracy(
        ["CODING", "MEETING", "RESEARCH"],
        ["CODING", "MEETING", "RESEARCH"],
    )
    assert result["accuracy"] == 1.0
    assert result["f1_score"] == 1.0
    print("✅")

    # ---- Test 6: Intent accuracy — partial ----
    print("Test 6: Intent accuracy partial... ", end="")
    result = mc.compute_intent_accuracy(
        ["CODING", "MEETING", "CODING", "ENTERTAINMENT"],
        ["CODING", "MEETING", "RESEARCH", "ENTERTAINMENT"],
    )
    assert result["accuracy"] == 0.75  # 3/4
    assert result["f1_score"] > 0.0
    print("✅")

    # ---- Test 7: Intent accuracy — empty ----
    print("Test 7: Intent accuracy empty... ", end="")
    result = mc.compute_intent_accuracy([], [])
    assert result["accuracy"] == 0.0
    print("✅")

    # ---- Test 8: WAR from KB ----
    print("Test 8: WAR from KB... ", end="")
    kb.log_workflow("CODING", "open vs code", "open VS Code",
                    {"steps": []}, confirmed=True, executed=True)
    kb.log_workflow("CODING", "open notepad", "open Notepad",
                    {"steps": []}, confirmed=False, executed=False)
    war = mc.compute_war()
    assert war["total"] == 2
    assert war["accepted"] == 1
    assert war["rate"] == 0.5
    print("✅")

    # ---- Test 9: ER from KB ----
    print("Test 9: ER from KB... ", end="")
    er = mc.compute_er()
    assert er["total_executed"] == 1
    assert er["successful"] == 1
    assert er["rate"] == 1.0
    print("✅")

    # ---- Test 10: Generate report ----
    print("Test 10: generate_report... ", end="")
    report = mc.generate_report()
    assert "PERFORMANCE METRICS REPORT" in report
    assert "Workflow Acceptance Rate" in report
    assert "Execution Reliability" in report
    assert "50.0%" in report  # WAR
    assert "100.0%" in report  # ER
    print("✅")

    kb.close()

    print(f"\n{'=' * 50}")
    print(f"  All Metrics tests passed! ✅")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    run_tests()
