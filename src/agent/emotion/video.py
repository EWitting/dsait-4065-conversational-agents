# from deepface import DeepFace
# import cv2
import time

#video emotion inference. ended up not being used due to bugs, but implementation is provided here anyways
class VideoSystem:
    def __init__(self):
        self.capture = None
        self.emotions = {"happy", "sad", "neutral", "disgust", "surprise"}#list of emotions for the sake of discretization

    def get_emotion(self, video=None, utterance_length=5):
        if video is None:
            capture = cv2.VideoCapture(0)
        else:
            capture = cv2.VideoCapture(video)#capture the videp

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
                analysis = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False) #using DeepFace to analyze emotion
                detectedEmotion = analysis[0].get('dominant_emotion', 'Unknown') #detect the emotion
                if detectedEmotion in self.emotions: #check if it is in the list
                    detectedEmotions.append(detectedEmotion)
            except Exception as e:
                print(f"Error: {e}. No face detected.")

        capture.release()
        cv2.destroyAllWindows()


        if detectedEmotions:
            return max(detectedEmotions, key=detectedEmotions.count) #return the emotion
        else:
            return None


"""
if __name__ == "__main__":
    video_system = VideoSystem()
    detected_emotion = video_system.get_emotion()

    print("Detected Emotion:", detected_emotion)
    """
