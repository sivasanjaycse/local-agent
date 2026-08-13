from faster_whisper import WhisperModel
import config


class WhisperTranscriber:

    def __init__(self):
        self.model = WhisperModel(
            config.WHISPER_MODEL,
            device=config.WHISPER_DEVICE,
            compute_type=config.WHISPER_COMPUTE_TYPE
        )

    def transcribe(self, audio_file):

        segments, info = self.model.transcribe(
            audio_file
        )

        text = " ".join(
            segment.text.strip()
            for segment in segments
        )

        return {
            "text": text,
            "language": info.language
        }
