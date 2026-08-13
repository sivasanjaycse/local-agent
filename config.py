import os
from dotenv import load_dotenv

load_dotenv()

# ==============================
# Gemini
# ==============================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-3.6-flash"


# ==============================
# Whisper
# ==============================

WHISPER_MODEL = "base"
WHISPER_DEVICE = "cpu"
WHISPER_COMPUTE_TYPE = "int8"


# ==============================
# Microphone
# ==============================

MICROPHONE_DEVICE_ID = 2
SAMPLE_RATE = 16000
RECORDING_DURATION = 5
