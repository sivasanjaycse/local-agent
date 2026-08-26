"""
Intent Recognition Module — Module 3

Serves as the cognitive core of the agent. Uses the Gemini LLM to
classify the user's UNDERLYING GOAL into high-level semantic intents
(e.g., Coding, Meeting, Research, Entertainment) and extract structured
entities — as described in Section III-A, Module 3 of the paper.

This replaces the previous action-level taxonomy (OPEN_APPLICATION,
WEB_SEARCH, etc.) with goal-level intents that support the paper's
"Understand-Reason-Recommend" paradigm.
"""

import json
from google import genai
from google.genai import types
import config


class GeminiIntentClassifier:

    def __init__(self):
        api_key = config.GEMINI_API_KEY

        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set")

        self.client = genai.Client(api_key=api_key)
        self.model = config.GEMINI_MODEL

    def classify(self, user_text):
        """
        Classify a preprocessed utterance into a high-level intent
        and extract structured entities.

        Args:
            user_text: Cleaned text from the NLU module.

        Returns:
            dict with keys: intent, entities, reasoning
        """

        prompt = f"""
You are the intent classifier for a Voice-Driven Intelligent Desktop
Workflow Agent running on Windows.

Your task is to understand the user's UNDERLYING GOAL — not just the
literal command — and classify it into exactly ONE of these high-level
intent categories:

1. CODING          — Software development, programming, building
                     projects, vibe coding, code review
2. MEETING         — Video calls, conferences, virtual meetings,
                     team discussions, joining calls
3. RESEARCH        — Information gathering, learning, searching for
                     tutorials, studying, reading documentation
4. ENTERTAINMENT   — Music, videos, gaming, relaxation, streaming
5. COMMUNICATION   — Email, messaging, social media, chatting
6. PRODUCTIVITY    — Note-taking, document editing, general browsing,
                     file management, organization
7. SYSTEM          — System-level operations: screenshots, folder
                     creation, settings, configuration

You must ALSO extract all relevant entities from the user's request.

Return ONLY valid JSON in this exact format:
{{
    "intent": "INTENT_NAME",
    "entities": {{
        "applications": [],
        "websites": [],
        "query": "",
        "topic": "",
        "action": "",
        "file_target": ""
    }},
    "reasoning": "Brief explanation of why this intent was chosen"
}}

Entity field descriptions:
- applications : Desktop apps mentioned or implied (VS Code, Chrome,
                 Notepad, Calculator). Use canonical names.
- websites     : Web services mentioned, each with "name" and "url".
                 Always provide correct, real URLs.
- query        : A search query if the user wants to look something up.
- topic        : The general subject or theme of the request.
- action       : The primary action verb (open, search, create_folder,
                 screenshot, open_folder).
- file_target  : File or folder name if applicable.

CLASSIFICATION RULES:
- Classify based on the user's GOAL, not the literal action verb.
  "Open VS Code"                → CODING (goal is to code)
  "Open YouTube"                → ENTERTAINMENT (goal is to watch)
  "Search for Python tutorials" → RESEARCH (goal is to learn)
  "Open Notepad"                → PRODUCTIVITY (goal is to take notes)
  "Open Chrome"                 → PRODUCTIVITY (general tool usage)
  "Let's do vibe coding"        → CODING (goal is to code with ambiance)
  "Take a screenshot"           → SYSTEM (system operation)
  "Create a folder"             → SYSTEM (system operation)
- For websites, ALWAYS provide the correct real URL.
- For CODING with "vibe coding", include Spotify, YouTube, Claude,
  Gemini, and ChatGPT in websites, plus VS Code in applications.
- If no specific app is mentioned for CODING, default to VS Code.

Examples:

User: "Let's start coding"
{{
    "intent": "CODING",
    "entities": {{
        "applications": ["VS Code"],
        "websites": [],
        "query": "",
        "topic": "coding session",
        "action": "open",
        "file_target": ""
    }},
    "reasoning": "User wants to begin a coding session"
}}

User: "Let's do vibe coding"
{{
    "intent": "CODING",
    "entities": {{
        "applications": ["VS Code"],
        "websites": [
            {{"name": "Spotify", "url": "https://open.spotify.com"}},
            {{"name": "YouTube", "url": "https://www.youtube.com"}},
            {{"name": "Claude", "url": "https://claude.ai"}},
            {{"name": "Gemini", "url": "https://gemini.google.com"}},
            {{"name": "ChatGPT", "url": "https://chatgpt.com"}}
        ],
        "query": "",
        "topic": "vibe coding session",
        "action": "open",
        "file_target": ""
    }},
    "reasoning": "User wants a coding session with music and AI tools"
}}

User: "Open VS Code"
{{
    "intent": "CODING",
    "entities": {{
        "applications": ["VS Code"],
        "websites": [],
        "query": "",
        "topic": "coding",
        "action": "open",
        "file_target": ""
    }},
    "reasoning": "Opening VS Code implies the user wants to code"
}}

User: "Open this folder in VS Code"
{{
    "intent": "CODING",
    "entities": {{
        "applications": ["VS Code"],
        "websites": [],
        "query": "",
        "topic": "coding",
        "action": "open_folder",
        "file_target": "."
    }},
    "reasoning": "User wants to code in the current folder"
}}

User: "Search YouTube for Python tutorials"
{{
    "intent": "RESEARCH",
    "entities": {{
        "applications": [],
        "websites": [{{"name": "YouTube", "url": "https://www.youtube.com"}}],
        "query": "Python tutorials",
        "topic": "Python learning",
        "action": "search",
        "file_target": ""
    }},
    "reasoning": "User wants to research Python by watching tutorials"
}}

User: "Open Chrome"
{{
    "intent": "PRODUCTIVITY",
    "entities": {{
        "applications": ["Chrome"],
        "websites": [],
        "query": "",
        "topic": "web browsing",
        "action": "open",
        "file_target": ""
    }},
    "reasoning": "Opening a general browser for productivity tasks"
}}

User: "Take a screenshot"
{{
    "intent": "SYSTEM",
    "entities": {{
        "applications": [],
        "websites": [],
        "query": "",
        "topic": "screenshot",
        "action": "screenshot",
        "file_target": ""
    }},
    "reasoning": "System-level screen capture operation"
}}

User: "Create a folder called Projects"
{{
    "intent": "SYSTEM",
    "entities": {{
        "applications": [],
        "websites": [],
        "query": "",
        "topic": "file management",
        "action": "create_folder",
        "file_target": "Projects"
    }},
    "reasoning": "System-level folder creation operation"
}}

User: "Open Spotify"
{{
    "intent": "ENTERTAINMENT",
    "entities": {{
        "applications": [],
        "websites": [{{"name": "Spotify", "url": "https://open.spotify.com"}}],
        "query": "",
        "topic": "music",
        "action": "open",
        "file_target": ""
    }},
    "reasoning": "User wants to listen to music for entertainment"
}}

User: "Open Notepad"
{{
    "intent": "PRODUCTIVITY",
    "entities": {{
        "applications": ["Notepad"],
        "websites": [],
        "query": "",
        "topic": "note-taking",
        "action": "open",
        "file_target": ""
    }},
    "reasoning": "User wants to take notes or edit text"
}}

User: "Open GitHub"
{{
    "intent": "CODING",
    "entities": {{
        "applications": [],
        "websites": [{{"name": "GitHub", "url": "https://github.com"}}],
        "query": "",
        "topic": "code repository",
        "action": "open",
        "file_target": ""
    }},
    "reasoning": "GitHub is a code repository — goal is coding"
}}

User: "I have a meeting to join"
{{
    "intent": "MEETING",
    "entities": {{
        "applications": [],
        "websites": [{{"name": "Google Meet", "url": "https://meet.google.com"}}],
        "query": "",
        "topic": "virtual meeting",
        "action": "open",
        "file_target": ""
    }},
    "reasoning": "User wants to join a virtual meeting"
}}

User: "Open Claude"
{{
    "intent": "CODING",
    "entities": {{
        "applications": [],
        "websites": [{{"name": "Claude", "url": "https://claude.ai"}}],
        "query": "",
        "topic": "AI assistant",
        "action": "open",
        "file_target": ""
    }},
    "reasoning": "Claude is an AI coding assistant — likely for coding"
}}

User request:
"{user_text}"
"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema={
                    "type": "object",
                    "properties": {
                        "intent": {
                            "type": "string",
                            "enum": [
                                "CODING",
                                "MEETING",
                                "RESEARCH",
                                "ENTERTAINMENT",
                                "COMMUNICATION",
                                "PRODUCTIVITY",
                                "SYSTEM",
                            ],
                        },
                        "entities": {
                            "type": "object",
                            "properties": {
                                "applications": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "websites": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "name": {
                                                "type": "string"
                                            },
                                            "url": {
                                                "type": "string"
                                            },
                                        },
                                        "required": ["name", "url"],
                                    },
                                },
                                "query": {"type": "string"},
                                "topic": {"type": "string"},
                                "action": {"type": "string"},
                                "file_target": {"type": "string"},
                            },
                        },
                        "reasoning": {"type": "string"},
                    },
                    "required": ["intent", "entities", "reasoning"],
                },
            ),
        )

        if not response.text:
            raise RuntimeError("Gemini returned an empty response")

        return json.loads(response.text)
