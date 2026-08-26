"""
Preference Learning Engine — Module 7

Continuous adaptation mechanism that ingests user feedback and
autonomously analyzes behavioral patterns to refine future
intent-to-workflow mappings.

Responsibilities (per paper Section III-A, Module 7):
  - Ingest implicit feedback (accepted/rejected workflows)
  - Record execution timestamps for temporal analysis
  - Update app and website usage profiles
  - Provide personalized recommendations to Module 4
  - Track acceptance trends over time

This module reads from and writes to the Knowledge Base (Module 8).
"""

from datetime import datetime


class PreferenceLearningEngine:
    """
    Bridges the pipeline's runtime events with the Knowledge Base,
    and exposes learned preferences for the Workflow Recommendation
    Module.
    """

    def __init__(self, knowledge_base):
        """
        Args:
            knowledge_base: A KnowledgeBase instance (Module 8).
        """
        self.kb = knowledge_base

    # ================================================================ #
    #  Recording interactions                                          #
    # ================================================================ #

    def record_interaction(
        self,
        nlu_result,
        intent_result,
        workflow,
        confirmed,
        executed=False,
        error=None,
    ):
        """
        Called at the end of every pipeline run to persist the
        interaction and update all usage counters.

        Args:
            nlu_result:    dict from NLUPreprocessor.process()
            intent_result: dict from GeminiIntentClassifier.classify()
            workflow:      dict from build_workflow()
            confirmed:     bool — did the user accept?
            executed:      bool — did execution succeed?
            error:         str or None — error message if execution failed
        """
        intent = intent_result.get("intent", "UNKNOWN")
        user_input = nlu_result.get("original_text", "")
        normalized = nlu_result.get("normalized_text", "")

        # 1. Log the full workflow event
        self.kb.log_workflow(
            intent=intent,
            user_input=user_input,
            normalized_input=normalized,
            workflow=workflow,
            confirmed=confirmed,
            executed=executed,
            error=error,
        )

        # 2. Update temporal preference (always — even for rejections,
        #    so we know what the user was *trying* to do at this time)
        self.kb.update_temporal_preference(intent)

        # 3. If confirmed and executed, update app/website usage
        if confirmed and executed and error is None:
            self._update_usage_from_workflow(workflow, intent)

    def _update_usage_from_workflow(self, workflow, intent):
        """Extract apps/websites from the executed workflow and
        update their usage counters."""
        for step in workflow.get("steps", []):
            action = step.get("action")

            if action == "OPEN_APPLICATION":
                app = step.get("target")
                if app:
                    self.kb.update_app_usage(app, intent)

            elif action == "OPEN_WEBSITE":
                name = step.get("target")
                url = step.get("url")
                if name and url:
                    self.kb.update_website_usage(name, url, intent)

    # ================================================================ #
    #  Recommendation queries                                          #
    # ================================================================ #

    def get_recommended_apps(self, intent, limit=5):
        """
        Return the most-used applications for the given intent,
        learned from historical executions.

        Returns:
            list[str] — application names ordered by frequency.
        """
        rows = self.kb.get_top_apps(intent, limit=limit)
        return [row["application"] for row in rows]

    def get_recommended_websites(self, intent, limit=5):
        """
        Return the most-used websites for the given intent,
        learned from historical executions.

        Returns:
            list[dict] with keys: name, url
        """
        rows = self.kb.get_top_websites(intent, limit=limit)
        return [
            {"name": row["website_name"], "url": row["website_url"]}
            for row in rows
        ]

    def get_temporal_suggestion(self):
        """
        Based on the current hour and day-of-week, return the
        most likely intent the user would want.

        Returns:
            str or None — e.g. "CODING" if that's the most common
            intent at this time, or None if insufficient data.
        """
        temporal = self.kb.get_temporal_intents()

        if temporal:
            return temporal[0]["intent"]

        return None

    def get_acceptance_trend(self, last_n=20):
        """
        Analyze the last N workflows to compute the acceptance rate
        trend.

        Returns:
            dict with keys:
                rate      — float 0.0–1.0
                accepted  — int count
                total     — int count
                trend     — str "improving", "declining", or "stable"
        """
        history = self.kb.get_recent_history(limit=last_n)

        if not history:
            return {
                "rate": 0.0,
                "accepted": 0,
                "total": 0,
                "trend": "stable",
            }

        total = len(history)
        accepted = sum(1 for h in history if h["confirmed"] == 1)
        rate = accepted / total if total > 0 else 0.0

        # Compute trend by comparing first half vs second half
        trend = "stable"
        if total >= 4:
            mid = total // 2
            # history is newest-first, so first half = recent
            recent_rate = sum(
                1 for h in history[:mid] if h["confirmed"] == 1
            ) / mid
            older_rate = sum(
                1 for h in history[mid:] if h["confirmed"] == 1
            ) / (total - mid)

            if recent_rate > older_rate + 0.1:
                trend = "improving"
            elif recent_rate < older_rate - 0.1:
                trend = "declining"

        return {
            "rate": round(rate, 3),
            "accepted": accepted,
            "total": total,
            "trend": trend,
        }
