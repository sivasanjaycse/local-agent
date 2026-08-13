try:
    from tests import bootstrap
except ModuleNotFoundError:
    import tests.bootstrap as bootstrap

from speech.microphone import MicrophoneRecorder


recorder = MicrophoneRecorder()

audio_file = recorder.record(
    duration=5,
    output_file="voice_test.wav"
)

print("\nAudio file:", audio_file)
