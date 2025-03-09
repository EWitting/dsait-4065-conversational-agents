import whisper
import warnings
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

class ASR:
    def __init__(self, model_name: str = "base"):
        self.model = whisper.load_model(model_name)  

    def transcribe(self, audio: str) -> str:
        result = self.model.transcribe(audio)
        return result.get("text", "")

"""
example use case:
asr_instance = ASR(model_name="base")

text = asr_instance.transcribe("test.mp3")
print("Transcribed text:", text)
"""

