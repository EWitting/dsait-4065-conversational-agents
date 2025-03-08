from deepface import DeepFace
import cv2
import time

class VideoSystem:
    def __init__(self):
        self.capture = None

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
                dominantEmotion = analysis[0].get('dominant_emotion', 'Unknown')
                detectedEmotions.append(dominantEmotion)
            except Exception as e:
                print(f"Error: {e}. No face detected.")

        capture.release()
        cv2.destroyAllWindows()


        if detectedEmotions:
            return max(detectedEmotions, key=detectedEmotions.count)
        else:
            return None






