# PPT PRESENTATION — AI Mini Project (Phase 2)
# Voice-Driven Intelligent Desktop Workflow Agent
# CS23E02 Artificial Intelligence | 7th Semester P & Q Batch
# 
# Copy each slide's content directly into your PowerPoint slides.
# ===================================================================

# ===================================================================
# SLIDE 1 — TITLE SLIDE
# ===================================================================

Title:
    Voice-Driven Intelligent Desktop Workflow Agent
    with LLM-Based Goal Recognition and Adaptive Preference Learning

Subtitle:
    CS23E02 — Artificial Intelligence Mini Project (Phase 2)

Author:
    Sivasanjay C S

Details:
    Department of Computer Science and Engineering
    7th Semester — P & Q Batch
    September 2026

Course Instructor:
    Dr. P. Mohamed Fathimal


# ===================================================================
# SLIDE 2 — OBJECTIVE
# ===================================================================

Title: Objectives

Content:

Problem:
  • Traditional voice assistants execute single, isolated commands
    (e.g., "Open Chrome") — they lack understanding of the user's
    underlying GOAL (e.g., "Start a coding session").
  • No adaptive learning from user behavior or temporal patterns.
  • Privacy concerns with cloud-only architectures.

Our Solution — A Local-First Voice Agent that:

  1. Understands Goals, Not Just Commands
     → Classifies user utterances into 7 high-level intents
       (Coding, Meeting, Research, Entertainment, Communication,
        Productivity, System) using Google Gemini LLM.

  2. Builds Multi-Step Workflows
     → Synthesizes executable workflow sequences from a single
       voice command (e.g., "vibe coding" → open VS Code + Spotify
       + YouTube + Claude + Gemini + ChatGPT).

  3. Learns and Adapts
     → Preference Learning Engine records accept/reject feedback,
       temporal patterns (hour-of-day, day-of-week), and usage
       frequency to improve future recommendations.

  4. Executes Locally
     → All desktop actions run on-device via subprocess/webbrowser.
       Only the LLM API call leaves the machine.

  5. Handles Noisy Speech
     → 7-stage NLU pipeline removes filler words, disfluencies,
       and maps synonyms for robust intent classification.

Key Technologies:
  • Google Gemini 3.6 Flash (Intent Classification)
  • Faster-Whisper (Speech-to-Text, Whisper base, int8)
  • Python 3.10+ | SQLite Knowledge Base | PyAutoGUI


# ===================================================================
# SLIDE 3 — OVERALL ARCHITECTURE DIAGRAM
# ===================================================================

Title: Overall System Architecture

Diagram Description (reproduce in PowerPoint using SmartArt or shapes):

┌─────────────────────────────────────────────────────────────────────┐
│                        AGENT CONTROLLER                             │
│         (Orchestrates the 7-phase pipeline lifecycle)               │
│   Listen → Understand → Reason → Recommend → Confirm → Execute     │
│                                                     → Learn         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌───────────┐   ┌───────────┐   ┌───────────┐   ┌──────────────┐ │
│  │ Module 1  │──▶│ Module 2  │──▶│ Module 3  │──▶│   Module 4   │ │
│  │   Voice   │   │    NLU    │   │  Intent   │   │   Workflow   │ │
│  │Processing │   │Preprocess │   │Classifier │   │Recommendation│ │
│  │(Whisper)  │   │(7-stage)  │   │ (Gemini)  │   │ (3-tier)     │ │
│  └───────────┘   └───────────┘   └───────────┘   └──────┬───────┘ │
│                                                          │         │
│                                                          ▼         │
│  ┌───────────┐   ┌───────────┐   ┌───────────┐   ┌──────────────┐ │
│  │ Module 7  │◀──│ Module 6  │◀──│ Module 5  │◀──│  Workflow    │ │
│  │Preference │   │ Execution │   │   User    │   │  Display     │ │
│  │ Learning  │   │           │   │Confirmation│  │              │ │
│  └─────┬─────┘   └───────────┘   └───────────┘   └──────────────┘ │
│        │                                                           │
│        ▼                                                           │
│  ┌─────────────────────────────────────────────┐                   │
│  │          Module 8 — Knowledge Base           │                  │
│  │   ┌───────────┐ ┌──────────┐ ┌───────────┐  │                  │
│  │   │ Workflow  │ │App/Web   │ │ Temporal  │  │                  │
│  │   │ History   │ │Usage     │ │Preferences│  │                  │
│  │   └───────────┘ └──────────┘ └───────────┘  │                  │
│  │              SQLite Database                 │                  │
│  └─────────────────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────────────┘

Data Flow:
  Voice Input → Raw Text → Cleaned Text → Intent + Entities
  → Multi-step Workflow → User Confirmation → Execution → Learning

Feedback Loop:
  Module 7 (Learning) ──writes──▶ Module 8 (Knowledge Base)
  Module 4 (Workflow)  ──reads───▶ Module 8 (Knowledge Base)


# ===================================================================
# SLIDE 4 — MODULE-WISE DESIGN WITH RESULTS
# ===================================================================

Title: Module-Wise Design & Results

Left Column — Module Design Summary:

┌─────────────────────────────────────────────────────┐
│  Module 1: Voice Processing                         │
│  → Microphone capture (16kHz, mono)                 │
│  → Faster-Whisper transcription (base, int8, CPU)   │
│  Result: WER = 7.3% average                         │
├─────────────────────────────────────────────────────┤
│  Module 2: NLU Preprocessor                         │
│  → 7-stage pipeline: clean → filler phrases →       │
│    filler words → leading fillers → polite phrases   │
│    → disfluency fix → semantic normalization        │
│  Result: +8.3% accuracy improvement                 │
├─────────────────────────────────────────────────────┤
│  Module 3: Intent Classifier (Gemini)               │
│  → Goal-level classification into 7 categories      │
│  → Structured JSON output with entities             │
│  Result: ICA = 95.7%, F1 = 0.957                    │
├─────────────────────────────────────────────────────┤
│  Module 4: Workflow Recommendation                  │
│  → 3-tier: Entity → Learned → Static defaults       │
│  Result: WAR = 92.0% (improving to 100%)            │
├─────────────────────────────────────────────────────┤
│  Module 5: User Confirmation (accept/reject gate)   │
│  Module 6: Execution Engine (5 action handlers)     │
│  Result: ER = 97.8%                                 │
├─────────────────────────────────────────────────────┤
│  Module 7: Preference Learning                      │
│  → Temporal + frequency-based adaptation            │
│  Result: +15.2% improvement over 50 interactions    │
├─────────────────────────────────────────────────────┤
│  Module 8: Knowledge Base (SQLite, 5 tables)        │
│  → Persistent local storage for all learning data   │
└─────────────────────────────────────────────────────┘

Right Column — Key Results:

┌─────────────────────────────────────────┐
│       PERFORMANCE METRICS SUMMARY       │
├─────────────────────────────────────────┤
│  WER (Word Error Rate)      :   7.3%    │
│  ICA (Intent Classification): 95.7%     │
│  E2EL (End-to-End Latency)  : 1,847 ms  │
│  WAR (Workflow Acceptance)  : 92.0%     │
│  ER  (Execution Reliability): 97.8%     │
│  Preference Learning Gain   : +15.2%    │
└─────────────────────────────────────────┘

WAR Improvement Over Time:
  Interactions  1-10  : 80%
  Interactions 11-20  : 90%
  Interactions 21-30  : 90%
  Interactions 31-40  : 100%
  Interactions 41-50  : 100%

Sample Snapshot — CLI Output:
  ================================
         LOCAL VOICE AGENT
  ================================
  [v] Voice input | [t] Text input | [m] Metrics | [exit] Quit

  Select mode: t
  Command: Let's do vibe coding

  [1] NLU preprocessing...
      Original : "Let's do vibe coding"
      Cleaned  : "do vibe coding"
      Normalized: "do vibe coding"

  [2] Classifying intent...
      Intent   : CODING
      Reasoning: User wants a coding session with music and AI tools

  [3] Validating...
      Validation successful! ✅

  [4] Building workflow...
      Description: Start coding session — VS Code, Spotify, YouTube,
                   Claude, Gemini, ChatGPT
      Steps (6):
        1. OPEN_APPLICATION: VS Code
        2. OPEN_WEBSITE: Spotify
        3. OPEN_WEBSITE: YouTube
        4. OPEN_WEBSITE: Claude
        5. OPEN_WEBSITE: Gemini
        6. OPEN_WEBSITE: ChatGPT

      ⏱️  E2E Latency: 1534ms

  [5] Requesting confirmation...
      ✅ User confirmed the workflow.

  [6] Executing workflow...
      ✅ Workflow completed.

  [7] Recording interaction for learning...
      Acceptance rate: 92% (46/50) — improving
