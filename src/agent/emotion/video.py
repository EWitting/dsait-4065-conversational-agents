# from deepface import DeepFace
# import cv2
import time

class VideoSystem:
    def __init__(self):
        self.capture = None
        self.emotions = {"happy", "sad", "neutral", "disgust", "surprise"}

    def get_emotion(self, video=None, utterance_length=5):
        if video is None:
            capture = cv2.VideoCapture(0)
        else:
            capture = cv2.VideoCapture(video)

        start = time.time()
        detectedEmotions = []

        while capture.isOpened():
            ret, frame = capture.read()
            if not ret:
                break

            elapsedTime = time.time() - start
            if elapsedTime >= utterance_length:
                break

            try:
                analysis = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
                detectedEmotion = analysis[0].get('dominant_emotion', 'Unknown')
                if detectedEmotion in self.emotions:
                    detectedEmotions.append(detectedEmotion)
            except Exception as e:
                print(f"Error: {e}. No face detected.")

        capture.release()
        cv2.destroyAllWindows()


        if detectedEmotions:
            return max(detectedEmotions, key=detectedEmotions.count)
        else:
            return None


"""
if __name__ == "__main__":
    video_system = VideoSystem()
    detected_emotion = video_system.get_emotion()

    print("Detected Emotion:", detected_emotion)
    """