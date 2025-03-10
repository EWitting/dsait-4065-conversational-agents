from dataclasses import dataclass
from .linguistic import LinguisticSystem
from .video import VideoSystem


@dataclass
class EmotionSystem:
    linguisticSystem: LinguisticSystem
    videoSystem: VideoSystem

    def __init__(self):
        self.linguisticSystem = LinguisticSystem()
        self.videoSystem = VideoSystem()

    def get_emotion(self, video, audio):
        linguistic_emotion = self.linguisticSystem.get_emotion(audio)
        video_emotion = self.videoSystem.get_emotion(video)
        return self.combine_emotions(linguistic_emotion, video_emotion)


    def combine_emotions(self, linguistic_emotion, video_emotion):
        if linguistic_emotion == video_emotion:
            return linguistic_emotion

        return linguistic_emotion, video_emotion