"""
NLU Preprocessor — Module 2

Sits between the Voice Processing Module (Module 1) and the
Intent Recognition Module (Module 3).

Responsibilities (per paper Section III-A, Module 2):
  - Semantic normalization of raw transcribed text
  - Filtering conversational filler words and disfluencies
  - Extracting core linguistic meaning
  - Passing structured, cleaned queries to the reasoning engine
"""

import re


class NLUPreprocessor:
    """
    Natural Language Understanding preprocessing layer.

    Converts noisy, conversational voice transcriptions into clean,
    normalized text suitable for LLM-based intent classification.
    """

    # ------------------------------------------------------------------ #
    #  Filler words safe to strip in any position                        #
    # ------------------------------------------------------------------ #
    FILLER_WORDS = {
        "um", "uh", "uhh", "umm", "umm",
        "hmm", "hm", "hmmm",
        "er", "err", "errm",
        "ah", "ahh", "oh", "ohh",
        "basically", "actually", "literally",
        "like",                       # almost always filler in commands
    }

    # ------------------------------------------------------------------ #
    #  Words that are fillers ONLY when they appear at the start         #
    # ------------------------------------------------------------------ #
    LEADING_FILLERS = {
        "well", "so", "okay", "ok", "alright",
        "hey", "hi", "hello", "yo",
        "anyway", "anyways",
        "yeah", "yep", "yup", "yes",
    }

    # ------------------------------------------------------------------ #
    #  Multi-word filler phrases (matched before single-word fillers)    #
    # ------------------------------------------------------------------ #
    FILLER_PHRASES = [
        "you know what i mean",
        "you know what",
        "you know",
        "i mean",
        "i guess",
        "i suppose",
        "i think",
        "let me think",
        "how do i say",
        "what's it called",
        "sort of",
        "kind of",
        "okay so",
        "so yeah",
        "yeah so",
    ]

    # ------------------------------------------------------------------ #
    #  Polite wrappers that add no semantic value for intent parsing     #
    # ------------------------------------------------------------------ #
    POLITE_PHRASES = [
        "could you please",
        "can you please",
        "would you please",
        "will you please",
        "please go ahead and",
        "go ahead and",
        "i'd like you to",
        "i would like you to",
        "i want you to",
        "i need you to",
        "could you",
        "can you",
        "would you",
        "will you",
        "i'd like to",
        "i would like to",
        "i want to",
        "i need to",
        "please",
    ]

    # ------------------------------------------------------------------ #
    #  Application name synonyms  →  canonical name                     #
    # ------------------------------------------------------------------ #
    APP_SYNONYMS = {
        "visual studio code": "VS Code",
        "vscode":             "VS Code",
        "v s code":           "VS Code",
        "vs-code":            "VS Code",
        "google chrome":      "Chrome",
        "chrome browser":     "Chrome",
        "the browser":        "Chrome",
        "note pad":           "Notepad",
        "calculator app":     "Calculator",
        "calc":               "Calculator",
    }

    # ------------------------------------------------------------------ #
    #  Action verb synonyms  →  canonical verb                          #
    # ------------------------------------------------------------------ #
    ACTION_SYNONYMS = {
        "launch":         "open",
        "start":          "open",
        "run":            "open",
        "fire up":        "open",
        "boot up":        "open",
        "bring up":       "open",
        "pull up":        "open",
        "start up":       "open",
        "look up":        "search",
        "google":         "search",
        "look for":       "search",
        "find me":        "search for",
        "grab a screenshot":   "take a screenshot",
        "capture screen":      "take a screenshot",
        "capture the screen":  "take a screenshot",
        "snap the screen":     "take a screenshot",
        "take a screen grab":  "take a screenshot",
        "make a folder":       "create a folder",
        "new folder":          "create a folder",
        "create directory":    "create a folder",
        "make directory":      "create a folder",
    }

    # ================================================================== #
    #  Public API                                                        #
    # ================================================================== #

    def process(self, raw_text):
        """
        Run the full NLU preprocessing pipeline.

        Args:
            raw_text: Raw transcription string from the Voice
                      Processing Module.

        Returns:
            dict with keys:
                original_text      – the unmodified input
                cleaned_text       – after filler/disfluency removal
                normalized_text    – after semantic synonym mapping
                is_valid           – False if nothing useful remains
                transformations    – list of steps that changed the text
        """
        if not raw_text or not raw_text.strip():
            return {
                "original_text":   raw_text,
                "cleaned_text":    "",
                "normalized_text": "",
                "is_valid":        False,
                "transformations": [],
            }

        transformations = []
        text = raw_text.strip()

        # 1. Basic text cleaning (lowercase, punctuation, whitespace)
        prev = text
        text = self._clean_text(text)
        if text != prev.lower().strip():
            transformations.append("text_cleaning")

        # 2. Remove multi-word filler phrases (before single words)
        prev = text
        text = self._remove_filler_phrases(text)
        if text != prev:
            transformations.append("filler_phrase_removal")

        # 3. Remove single filler words
        prev = text
        text = self._remove_filler_words(text)
        if text != prev:
            transformations.append("filler_word_removal")

        # 4. Strip leading-only fillers
        prev = text
        text = self._remove_leading_fillers(text)
        if text != prev:
            transformations.append("leading_filler_removal")

        # 5. Strip polite wrappers
        prev = text
        text = self._remove_polite_phrases(text)
        if text != prev:
            transformations.append("polite_phrase_removal")

        # 6. Fix disfluencies (repeated words, false starts)
        prev = text
        text = self._fix_disfluencies(text)
        if text != prev:
            transformations.append("disfluency_correction")

        cleaned_text = text.strip()

        # 7. Semantic normalization (action & app synonyms)
        normalized_text = self._normalize_semantics(cleaned_text)
        if normalized_text != cleaned_text:
            transformations.append("semantic_normalization")

        # 8. Final artifact cleanup
        normalized_text = self._final_cleanup(normalized_text)

        return {
            "original_text":   raw_text,
            "cleaned_text":    cleaned_text,
            "normalized_text": normalized_text,
            "is_valid":        bool(normalized_text.strip()),
            "transformations": transformations,
        }

    # ================================================================== #
    #  Pipeline stages                                                   #
    # ================================================================== #

    def _clean_text(self, text):
        """Lowercase, collapse whitespace, strip meaningless punctuation."""
        text = text.lower().strip()

        # Collapse repeated punctuation
        text = re.sub(r"[.]{2,}", ".", text)
        text = re.sub(r"[!]{2,}", "!", text)
        text = re.sub(r"[?]{2,}", "?", text)

        # Remove trailing sentence-end punctuation (adds nothing for
        # intent classification)
        text = text.rstrip(".!?")

        # Normalize whitespace
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    def _remove_filler_phrases(self, text):
        """Remove multi-word filler phrases via pattern matching."""
        for phrase in self.FILLER_PHRASES:
            pattern = r"\b" + re.escape(phrase) + r"\b"
            text = re.sub(pattern, " ", text, flags=re.IGNORECASE)

        return re.sub(r"\s+", " ", text).strip()

    def _remove_filler_words(self, text):
        """Remove single-word fillers from any position."""
        words = text.split()
        filtered = []

        for word in words:
            bare = word.strip(".,!?;:")
            if bare.lower() not in self.FILLER_WORDS:
                filtered.append(word)

        return " ".join(filtered)

    def _remove_leading_fillers(self, text):
        """Strip filler words that only count at sentence start."""
        words = text.split()

        while words and words[0].strip(".,!?;:").lower() in self.LEADING_FILLERS:
            words.pop(0)

        return " ".join(words)

    def _remove_polite_phrases(self, text):
        """Strip polite wrappers that add no intent information."""
        for phrase in self.POLITE_PHRASES:
            pattern = r"\b" + re.escape(phrase) + r"\b"
            text = re.sub(pattern, " ", text, flags=re.IGNORECASE)

        return re.sub(r"\s+", " ", text).strip()

    def _fix_disfluencies(self, text):
        """Fix repeated words and false starts from speech."""
        # "open open chrome"  →  "open chrome"
        text = re.sub(
            r"\b(\w+)(\s+\1)+\b", r"\1", text, flags=re.IGNORECASE
        )

        # "open ch- chrome"  →  "open chrome"
        text = re.sub(r"\b\w+-\s+", "", text)

        return re.sub(r"\s+", " ", text).strip()

    def _normalize_semantics(self, text):
        """Map synonyms to canonical terms (apps first, then actions)."""
        result = text

        # App name synonyms first — longest match first so that
        # "google chrome" is consumed before "google" can match
        # as an action synonym.
        for synonym, canonical in sorted(
            self.APP_SYNONYMS.items(),
            key=lambda item: len(item[0]),
            reverse=True,
        ):
            pattern = r"\b" + re.escape(synonym) + r"\b"
            result = re.sub(
                pattern, canonical, result, flags=re.IGNORECASE
            )

        # Action synonyms – longest match first
        for synonym, canonical in sorted(
            self.ACTION_SYNONYMS.items(),
            key=lambda item: len(item[0]),
            reverse=True,
        ):
            pattern = r"\b" + re.escape(synonym) + r"\b"
            result = re.sub(
                pattern, canonical, result, flags=re.IGNORECASE
            )

        return result

    def _final_cleanup(self, text):
        """Remove artifacts left by earlier stages."""
        # Collapse whitespace
        text = re.sub(r"\s+", " ", text)

        # Remove orphaned leading conjunctions / articles
        text = re.sub(
            r"^(and|but|then|the|a|an)\s+", "", text, flags=re.IGNORECASE
        )

        # Remove dangling commas
        text = re.sub(r",\s*,", ",", text)
        text = re.sub(r"^\s*,\s*", "", text)
        text = re.sub(r"\s*,\s*$", "", text)

        return text.strip()
