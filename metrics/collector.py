"""
Performance Metrics Collector

Provides quantitative evaluation metrics as defined in the paper
(Section III-D):

  1. WER  — Word Error Rate (transcription accuracy)
  2. ICA  — Intent Classification Accuracy & F1-Score
  3. E2EL — End-to-End Latency
  4. WAR  — Workflow Acceptance Rate
  5. ER   — Execution Reliability
"""

from datetime import datetime


class MetricsCollector:
    """Collects and reports performance metrics from the Knowledge Base."""

    def __init__(self, knowledge_base):
        """
        Args:
            knowledge_base: A KnowledgeBase instance (Module 8).
        """
        self.kb = knowledge_base

    # ================================================================ #
    #  WER — Word Error Rate                                           #
    # ================================================================ #

    @staticmethod
    def compute_wer(reference, hypothesis):
        """
        Compute Word Error Rate between a reference transcript
        and the ASR hypothesis using the standard edit-distance
        formula:  WER = (S + D + I) / N

        Args:
            reference:  str — the ground-truth transcript.
            hypothesis: str — the ASR output.

        Returns:
            float — WER as a ratio (0.0 = perfect, >1.0 possible).
        """
        ref_words = reference.lower().split()
        hyp_words = hypothesis.lower().split()

        n = len(ref_words)
        m = len(hyp_words)

        if n == 0:
            return 1.0 if m > 0 else 0.0

        # Levenshtein distance matrix
        dp = [[0] * (m + 1) for _ in range(n + 1)]

        for i in range(n + 1):
            dp[i][0] = i
        for j in range(m + 1):
            dp[0][j] = j

        for i in range(1, n + 1):
            for j in range(1, m + 1):
                if ref_words[i - 1] == hyp_words[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    dp[i][j] = 1 + min(
                        dp[i - 1][j],       # deletion
                        dp[i][j - 1],       # insertion
                        dp[i - 1][j - 1],   # substitution
                    )

        return dp[n][m] / n

    # ================================================================ #
    #  Intent Classification Accuracy & F1                             #
    # ================================================================ #

    @staticmethod
    def compute_intent_accuracy(predictions, labels):
        """
        Compute accuracy and macro F1-score for intent classification.

        Args:
            predictions: list[str] — predicted intent labels.
            labels:      list[str] — ground-truth intent labels.

        Returns:
            dict with keys: accuracy, f1_score, per_class
        """
        if not predictions or not labels:
            return {"accuracy": 0.0, "f1_score": 0.0, "per_class": {}}

        total = len(labels)
        correct = sum(
            1 for p, l in zip(predictions, labels) if p == l
        )
        accuracy = correct / total

        # Per-class precision, recall, F1
        all_classes = set(labels) | set(predictions)
        per_class = {}
        f1_scores = []

        for cls in all_classes:
            tp = sum(1 for p, l in zip(predictions, labels)
                     if p == cls and l == cls)
            fp = sum(1 for p, l in zip(predictions, labels)
                     if p == cls and l != cls)
            fn = sum(1 for p, l in zip(predictions, labels)
                     if p != cls and l == cls)

            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = (
                2 * precision * recall / (precision + recall)
                if (precision + recall) > 0
                else 0.0
            )

            per_class[cls] = {
                "precision": round(precision, 3),
                "recall": round(recall, 3),
                "f1": round(f1, 3),
            }
            f1_scores.append(f1)

        macro_f1 = sum(f1_scores) / len(f1_scores) if f1_scores else 0.0

        return {
            "accuracy": round(accuracy, 3),
            "f1_score": round(macro_f1, 3),
            "per_class": per_class,
        }

    # ================================================================ #
    #  WAR — Workflow Acceptance Rate (from KB)                        #
    # ================================================================ #

    def compute_war(self):
        """
        Workflow Acceptance Rate: accepted / total recommended.

        Returns:
            dict with keys: accepted, total, rate
        """
        return self.kb.get_workflow_acceptance_rate()

    # ================================================================ #
    #  ER — Execution Reliability (from KB)                            #
    # ================================================================ #

    def compute_er(self):
        """
        Execution Reliability: successful / total executed.

        Returns:
            dict with keys: successful, total_executed, rate
        """
        return self.kb.get_execution_reliability()

    # ================================================================ #
    #  Report                                                          #
    # ================================================================ #

    def generate_report(self):
        """
        Generate a formatted summary of all available metrics.

        Returns:
            str — multi-line formatted report.
        """
        war = self.compute_war()
        er = self.compute_er()

        lines = [
            "",
            "=" * 50,
            "  PERFORMANCE METRICS REPORT",
            "=" * 50,
            "",
            f"  Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "  Workflow Acceptance Rate (WAR)",
            "  ─────────────────────────────",
            f"    Accepted : {war['accepted']}",
            f"    Total    : {war['total']}",
            f"    Rate     : {war['rate']:.1%}",
            "",
            "  Execution Reliability (ER)",
            "  ──────────────────────────",
            f"    Successful    : {er['successful']}",
            f"    Total Executed: {er['total_executed']}",
            f"    Rate          : {er['rate']:.1%}",
            "",
            "  Note: WER and Intent F1 require labeled test data.",
            "  Use compute_wer() and compute_intent_accuracy()",
            "  with ground-truth corpora for those metrics.",
            "",
            "=" * 50,
        ]

        # Add recent history summary
        history = self.kb.get_recent_history(limit=10)
        if history:
            lines.append("")
            lines.append("  Recent Workflow History (last 10)")
            lines.append("  ─────────────────────────────────")
            for h in history:
                status = "✅" if h["confirmed"] else "❌"
                exec_status = ""
                if h["confirmed"]:
                    if h["executed"] and not h["execution_error"]:
                        exec_status = " → ran OK"
                    elif h["execution_error"]:
                        exec_status = f" → ERROR: {h['execution_error']}"
                lines.append(
                    f"    {status} [{h['intent']}] "
                    f"\"{h['user_input']}\"{exec_status}"
                )
            lines.append("")

        return "\n".join(lines)
