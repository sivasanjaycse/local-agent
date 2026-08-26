from agent.controller import AgentController
from speech.microphone import MicrophoneRecorder
from speech.whisper_transcriber import WhisperTranscriber
from metrics.collector import MetricsCollector
import config


def main():

    print("================================")
    print("       LOCAL VOICE AGENT")
    print("================================")

    controller = AgentController()
    recorder = MicrophoneRecorder()
    transcriber = WhisperTranscriber()
    metrics = MetricsCollector(controller.kb)

    while True:

        print("\n[v] Voice input  |  [t] Text input  |  [m] Metrics  |  [exit] Quit")

        mode = input("\nSelect mode: ").strip().lower()

        if mode == "exit":
            print("\nGoodbye! 👋")
            break

        if mode == "m":
            report = metrics.generate_report()
            print(report)
            continue

        user_text = None

        if mode == "v":
            try:
                print("\n🎤 Listening...")
                audio_file = recorder.record(
                    duration=config.RECORDING_DURATION
                )

                print("📝 Transcribing...")
                result = transcriber.transcribe(audio_file)
                user_text = result["text"]

                print(f"\n🗣️  You said: \"{user_text}\"")

                if not user_text.strip():
                    print("Could not understand. Please try again.")
                    continue

            except Exception as e:
                print(f"\n❌ Voice input error: {e}")
                continue

        elif mode == "t":
            user_text = input("\nCommand: ")

        else:
            print("Invalid mode. Please enter 'v', 't', 'm', or 'exit'.")
            continue

        if not user_text or not user_text.strip():
            print("Please enter a command.")
            continue

        try:
            result = controller.process_text(user_text)

            print("\nResult:")
            print(result)

        except Exception as e:
            print("\n❌ Error:")
            print(e)


if __name__ == "__main__":
    main()
