from dataclasses import dataclass
from .linguistic import LinguisticSystem
from .video import VideoSystem
from collections import Counter

@dataclass
class EmotionSystem:
    linguisticSystem: LinguisticSystem
    videoSystem: VideoSystem

    def __init__(self):
        self.linguisticSystem = LinguisticSystem()
        self.videoSystem = VideoSystem()

    def get_emotion(self, video, audio):
        linguistic_emotion = self.linguisticSystem.get_emotion(audio)
        video_emotions = self.videoSystem.get_emotion(video)

        if video_emotions:
            # Get the most common emotion detected in the video frames
            video_emotion = self.get_most_common_emotion(video_emotions)
        else:
            video_emotion = "Unknown"

        return self.combine_emotions(linguistic_emotion, video_emotion)

    def get_most_common_emotion(self, emotions_list):
        # Use Counter to find the most common emotion from the list
        emotion_counts = Counter(emotions_list)
        most_common_emotion, _ = emotion_counts.most_common(1)[0]
        return most_common_emotion

    def combine_emotions(self, linguistic_emotion, video_emotion):
        if linguistic_emotion == video_emotion:
            return linguistic_emotion

        return "Mixed"