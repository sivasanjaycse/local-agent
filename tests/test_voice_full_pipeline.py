try:
    from tests import bootstrap
except ModuleNotFoundError:
    import tests.bootstrap as bootstrap

from speech.microphone import MicrophoneRecorder
from speech.whisper_transcriber import WhisperTranscriber
from llm.gemini_client import GeminiIntentClassifier
from validation.intent_validator import validate_intent
from workflows.workflow_builder import build_workflow
from confirmation.confirm import request_confirmation
from execution.executor import execute_workflow


recorder = MicrophoneRecorder()
transcriber = WhisperTranscriber()
classifier = GeminiIntentClassifier()


# 1. Record voice
print("🎤 Speak your command...")

audio_file = recorder.record(
    duration=5,
    output_file="voice_command.wav"
)


# 2. Transcribe
print("\n🧠 Transcribing...")

transcription = transcriber.transcribe(audio_file)
user_text = transcription["text"]

print("\nRecognized text:")
print(user_text)


# 3. Gemini
print("\n🤖 Sending to Gemini...")

intent_result = classifier.classify(user_text)

print("\nGemini result:")
print(intent_result)


# 4. Validate
print("\n🛡️ Validating...")

validate_intent(intent_result)

print("Validation successful! ✅")


# 5. Build workflow
print("\n📋 Building workflow...")

workflow = build_workflow(intent_result)

print("Workflow:")
print(workflow)


# 6. Confirmation
print("\n👤 Requesting confirmation...")

confirmed = request_confirmation(workflow)

if not confirmed:
    print("\n❌ User rejected the workflow.")
    print("Execution cancelled.")
    raise SystemExit(0)


# 7. Execute
print("\n⚙️ Executing workflow...")

execute_workflow(workflow)

print("\n✅ Workflow completed!")
