
from transformers import pipeline

class LinguisticSystem:
    def __init__(self):
        self.emotion = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base") #feed the text to the classifier to infer emotion


    def get_emotion(self, text):
        emotion = self.emotion(text)#usage of the function
        if not emotion:
            return "Unknown"
        else:
            return emotion[0].get('label', 'Unknown')#return the emotion

