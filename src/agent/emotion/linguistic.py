
from transformers import pipeline
import whisper
from src.agent.asr import asr

class LinguisticSystem:
    def __init__(self):
        self.asr = asr.ASR()
        self.emotion = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base")


    def get_emotion(self, audio):
        transcription = self.asr.transcribe(audio)
        emotion = self.emotion(transcription)
        if not emotion:
            return "Unknown"
        else:
            return emotion[0].get('label', 'Unknown')


"""
if __name__ == "__main__":
    audio = "/Users/shivangikachole/PycharmProjects/dsait-4065-conversational-agents/src/agent/emotion/test.mp3"
    video_system = LinguisticSystem()
    detected_emotion = video_system.get_emotion(audio)

    print("Detected Emotion:", detected_emotion)
    """







