import cv2
from deepface import DeepFace
from collections import Counter


class VideoSystem:
    def __init__(self):
        pass

    def get_emotion(self, video):
        video_capture = cv2.VideoCapture(video)  # Load video file

        if not video_capture.isOpened():
            print("Error: Could not open video file.")
            return None, None

        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        emotions_detected = []

        while True:
            ret, frame = video_capture.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            for (x, y, w, h) in faces:
                face = frame[y:y + h, x:x + w]

                try:
                    analysis = DeepFace.analyze(face, actions=['emotion'], enforce_detection=False)
                    emotion = analysis[0]['dominant_emotion']
                    emotions_detected.append(emotion)
                except:
                    pass

        video_capture.release()

        most_common_emotion = None
        if emotions_detected:
            most_common_emotion = Counter(emotions_detected).most_common(1)[0][0]

        return most_common_emotion


"""
if __name__ == "__main__":
    vs = VideoSystem()
    emotions, common_emotion = vs.get_emotion("/Users/shivangikachole/PycharmProjects/dsait-4065-conversational-agents/src/agent/emotion/test.mov")  # Replace with actual video file path
    print("Detected Emotions:", emotions)
    print("Most Common Emotion:", common_emotion)
    """
