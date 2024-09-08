from faster_whisper import WhisperModel
import os


class STT:
    def __init__(self, model_size="tiny", device="cpu", num_workers=4):
        """
        Initialize the STT class with the specified model size and device.

        Parameters:
        model_size (str): The size of the Whisper model to use (e.g., "tiny", "base", "small", "medium", "large").
                            for english only: "tiny.en", "base.en", "small.en", "medium.en" are available and perform better.
        device (str): The device to run the model on ("cpu" or "cuda").
        """
        self.model_size = model_size
        self.device = device
        self.model = None
        self.num_workers = num_workers
        self._load_model()

    def _load_model(self):
        """
        Load the Whisper model. The model will be downloaded if it is not already cached locally.
        """
        self.model = WhisperModel(self.model_size, device=self.device, num_workers=self.num_workers)

    def format_time(self, seconds):
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        milliseconds = (seconds - int(seconds)) * 1000
        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d},{int(milliseconds):03d}"

    def transcribe(self, input_file):
        segments, info = self.model.transcribe(input_file, vad_filter=True, beam_size=5)
        print("Detected language '{}' with probability {:.2f}".format(info.language, info.language_probability))

        return segments

    def get_srt(self, segments):
        try:
            srt_dict = {}
            for segment in segments:
                start_time = self.format_time(segment.start)
                end_time = self.format_time(segment.end)
                text = segment.text
                segment_id = segment.id
                line_out = f"{segment_id}\n{start_time} --> {end_time}\n{text.lstrip()}\n\n"
                srt_dict[segment_id] = line_out

        except Exception as e:
            print(f"An error occured: {e}")

        return srt_dict
    
    def write_srt_to_file(self, srt_dict, srt_path):
        try:
            with open(srt_path, 'w', encoding='utf-8') as srt_file:
                for key in sorted(srt_dict.keys()):
                    srt_file.write(srt_dict[key])
        except Exception as e:
            print(f"An error occured when writing srt to file: {e}")

