from transformers import pipeline
from src.agent.asr import asr

class LinguisticSystem:
    def __init__(self):
        self.asr = asr.ASR()
        self.emotion = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base")

    def get_emotion(self, audio):
        transcription = self.asr.transcribe(audio)
        try:
            emotion = self.emotion(transcription)
            if not emotion:
                return "Unknown"
            else:
                return emotion[0].get('label', 'Unknown')
        except Exception as e:
            print(f"Error in emotion detection: {e}")
            return "Unknown"





