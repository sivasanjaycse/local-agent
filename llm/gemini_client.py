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
                                "SYSTEM_ACTION"
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
                                        "Calculator"
                                    ]
                                },
                                "query": {"type": "string"},
                                "website": {"type": "string"},
                                "operation": {"type": "string"},
                                "name": {"type": "string"},
                                "action": {"type": "string"}
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
