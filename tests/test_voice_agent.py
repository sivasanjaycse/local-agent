try:
    from tests import bootstrap
except ModuleNotFoundError:
    import tests.bootstrap as bootstrap

from speech.microphone import MicrophoneRecorder
from speech.whisper_transcriber import WhisperTranscriber
from llm.gemini_client import GeminiIntentClassifier


recorder = MicrophoneRecorder()
transcriber = WhisperTranscriber()
classifier = GeminiIntentClassifier()


print("🎤 Speak your command...")

audio_file = recorder.record(
    duration=5,
    output_file="voice_command.wav"
)

print("\n🧠 Transcribing...")

transcription = transcriber.transcribe(audio_file)

user_text = transcription["text"]

print("\nRecognized text:")
print(user_text)

print("\n🤖 Sending text to Gemini...")

intent_result = classifier.classify(user_text)

print("\nGemini result:")
print(intent_result)
