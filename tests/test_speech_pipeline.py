try:
    from tests import bootstrap
except ModuleNotFoundError:
    import tests.bootstrap as bootstrap

from speech.microphone import MicrophoneRecorder
from speech.whisper_transcriber import WhisperTranscriber


recorder = MicrophoneRecorder()
transcriber = WhisperTranscriber()

print("🎤 Speak your command...")

audio_file = recorder.record(
    duration=5,
    output_file="voice_command.wav"
)

print("\n🧠 Transcribing...")

result = transcriber.transcribe(audio_file)

print("\nRecognized text:")
print(result["text"])

print("\nDetected language:")
print(result["language"])
