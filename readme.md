# local-agent

A voice-driven, local-first desktop workflow agent. It listens to (or reads) a
command, classifies your intent with an LLM, builds a workflow, asks you to
confirm it, then executes it on your machine — logging every step to a local
SQLite knowledge base.

Pipeline: **Voice/Text → NLU → Intent Classification (Gemini) → Workflow Build
→ User Confirmation → Execution → Knowledge Base Logging**

## Requirements

- Python 3.10+
- A Gemini API key ([Google AI Studio](https://aistudio.google.com/apikey))
- Windows recommended (execution layer uses PowerShell/Windows app paths);
  Linux is a secondary target
- A working microphone if you want to use voice mode

## Setup

1. **Clone the repo**
   ```bash
   git clone https://github.com/sivasanjaycse/local-agent.git
   cd local-agent
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your API key**

   Create a `.env` file in the project root (this file is git-ignored, so
   your key never gets committed):
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

   Other runtime settings (Whisper model size, microphone device ID, sample
   rate, recording duration) live in `config.py` — adjust `MICROPHONE_DEVICE_ID`
   if `v` mode picks up the wrong input device.

## Running the agent

```bash
python main.py
```

You'll get an interactive prompt:

| Mode | What it does |
|------|---------------|
| `v` | Record a short voice command (uses faster-whisper to transcribe it) |
| `t` | Type a text command instead of speaking |
| `m` | Print a metrics report (WAR, ER, etc.) from the knowledge base |
| `exit` | Quit |

Example (text mode):
```
Select mode: t
Command: open vs code and check my github
```
The agent will classify the intent, propose a workflow, ask you to confirm
(yes/no), then execute it if you accept. Every interaction — accepted or
rejected — is logged to `knowledge.db`.

## Currently supported intents

- `OPEN_APPLICATION`
- `WEB_SEARCH`
- `FILE_OPERATION`
- `SYSTEM_ACTION`

## Running tests

```bash
pip install pytest
pytest tests/
```

## Project structure

```
agent/        - AgentController: orchestrates the end-to-end pipeline
speech/       - microphone recording + faster-whisper transcription
nlu/          - text normalization / preprocessing
llm/          - Gemini-based intent classifier
validation/   - validates classified intent + extracted parameters
workflows/    - builds the structured workflow from an intent
confirmation/ - user confirmation gate before execution
execution/    - runs the confirmed workflow (opens apps, searches, etc.)
learning/     - preference learning from accept/reject history
knowledge/    - SQLite-backed knowledge base (knowledge.db)
metrics/      - computes WAR, ER, and other metrics from the knowledge base
tests/        - pytest test suite
main.py       - interactive CLI entry point
config.py     - runtime configuration (loads .env)
```

## Notes

- `knowledge.db` and `.env` are local state — don't commit real API keys or
  personal usage history if you fork this publicly.
- Voice mode requires `faster-whisper` model weights to download on first
  run; text mode (`t`) works immediately with no extra download.