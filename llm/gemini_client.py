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

        prompt = f"""
You are an intent classifier for a Windows desktop assistant.

Classify the user's request into exactly ONE of these intents:

1. OPEN_APPLICATION
2. WEB_SEARCH
3. FILE_OPERATION
4. SYSTEM_ACTION
5. OPEN_WEBSITE
6. VIBE_CODING

Return ONLY valid JSON.

Required format:
{{
    "intent": "INTENT_NAME",
    "parameters": {{}}
}}

Examples:

User: "Open Chrome"

{{
    "intent": "OPEN_APPLICATION",
    "parameters": {{
        "application": "Chrome"
    }}
}}

User: "Open VS Code"

{{
    "intent": "OPEN_APPLICATION",
    "parameters": {{
        "application": "VS Code"
    }}
}}

User: "Open this folder in VS Code"

{{
    "intent": "OPEN_APPLICATION",
    "parameters": {{
        "application": "VS Code",
        "open_folder": true
    }}
}}

User: "Search YouTube for Python tutorials"

{{
    "intent": "WEB_SEARCH",
    "parameters": {{
        "query": "Python tutorials",
        "website": "YouTube"
    }}
}}

User: "Create a folder called Projects"

{{
    "intent": "FILE_OPERATION",
    "parameters": {{
        "operation": "create_folder",
        "name": "Projects"
    }}
}}

User: "Take a screenshot"

{{
    "intent": "SYSTEM_ACTION",
    "parameters": {{
        "action": "screenshot"
    }}
}}

User: "Open Spotify"

{{
    "intent": "OPEN_WEBSITE",
    "parameters": {{
        "website": "Spotify",
        "url": "https://open.spotify.com"
    }}
}}

User: "Open Claude"

{{
    "intent": "OPEN_WEBSITE",
    "parameters": {{
        "website": "Claude",
        "url": "https://claude.ai"
    }}
}}

User: "Open GitHub"

{{
    "intent": "OPEN_WEBSITE",
    "parameters": {{
        "website": "GitHub",
        "url": "https://github.com"
    }}
}}

User: "Let's do vibe coding"

{{
    "intent": "VIBE_CODING",
    "parameters": {{
        "websites": [
            {{"website": "Spotify", "url": "https://open.spotify.com"}},
            {{"website": "YouTube", "url": "https://www.youtube.com"}},
            {{"website": "Claude", "url": "https://claude.ai"}},
            {{"website": "Gemini", "url": "https://gemini.google.com"}},
            {{"website": "ChatGPT", "url": "https://chatgpt.com"}}
        ]
    }}
}}

IMPORTANT RULES:
- For OPEN_WEBSITE, you MUST provide the correct, real URL for the website.
- For VIBE_CODING, always include Spotify, YouTube, Claude, Gemini, and ChatGPT with their correct URLs.
- OPEN_APPLICATION is for desktop apps like Chrome, Notepad, Calculator, VS Code.
- OPEN_WEBSITE is for websites/web services that open in the browser.

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
                                "OPEN_APPLICATION",
                                "WEB_SEARCH",
                                "FILE_OPERATION",
                                "SYSTEM_ACTION",
                                "OPEN_WEBSITE",
                                "VIBE_CODING"
                            ]
                        },
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "application": {
                                    "type": "string",
                                    "enum": [
                                        "Google Chrome",
                                        "Chrome",
                                        "Notepad",
                                        "Calculator",
                                        "VS Code"
                                    ]
                                },
                                "open_folder": {
                                    "type": "boolean"
                                },
                                "query": {"type": "string"},
                                "website": {"type": "string"},
                                "url": {"type": "string"},
                                "operation": {"type": "string"},
                                "name": {"type": "string"},
                                "action": {"type": "string"},
                                "websites": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "website": {
                                                "type": "string"
                                            },
                                            "url": {
                                                "type": "string"
                                            }
                                        },
                                        "required": [
                                            "website",
                                            "url"
                                        ]
                                    }
                                }
                            }
                        }
                    },
                    "required": ["intent", "parameters"]
                }
            )
        )

        if not response.text:
            raise RuntimeError("Gemini returned an empty response")

        return json.loads(response.text)
