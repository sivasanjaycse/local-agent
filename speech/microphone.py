import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import config


class MicrophoneRecorder:

    def __init__(
        self,
        device_id=config.MICROPHONE_DEVICE_ID,
        sample_rate=config.SAMPLE_RATE
    ):
        self.device_id = device_id
        self.sample_rate = sample_rate

    def record(self, duration=5, output_file="recording.wav"):

        print(f"Recording for {duration} seconds... 🎤")

        audio = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,
            dtype=np.int16,
            device=self.device_id
        )

        sd.wait()

        write(
            output_file,
            self.sample_rate,
            audio
        )

        print(f"Recording saved: {output_file}")

        return output_file
