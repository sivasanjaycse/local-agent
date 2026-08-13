try:
    from tests import bootstrap
except ModuleNotFoundError:
    import tests.bootstrap as bootstrap

import config


print("Gemini model:", config.GEMINI_MODEL)

print("Whisper model:", config.WHISPER_MODEL)
print("Whisper device:", config.WHISPER_DEVICE)

print("Microphone device:", config.MICROPHONE_DEVICE_ID)
print("Sample rate:", config.SAMPLE_RATE)
print("Recording duration:", config.RECORDING_DURATION)

print("\nConfiguration loaded successfully! ✅")
