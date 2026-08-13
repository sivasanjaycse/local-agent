try:
    from tests import bootstrap
except ModuleNotFoundError:
    import tests.bootstrap as bootstrap

from speech.whisper_transcriber import WhisperTranscriber


transcriber = WhisperTranscriber()

result = transcriber.transcribe(
    "voice_test.wav"
)

print("Transcription:")
print(result["text"])

print("\nLanguage:")
print(result["language"])
