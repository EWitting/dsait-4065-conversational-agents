from deepface import DeepFace
import cv2

class VideoSystem:
    def __init__(self):
        pass  # No need to initialize webcam if using a recorded video

    def get_emotion(self, video_path):
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            print("Error: Could not open video file.")
            return None

        emotions_detected = []  # Store detected emotions

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break  # Stop when video ends

            try:
                # Perform emotion analysis with error handling
                analysis = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
                if isinstance(analysis, list) and 'dominant_emotion' in analysis[0]:
                    dominant_emotion = analysis[0]['dominant_emotion']
                    emotions_detected.append(dominant_emotion)
                    print(f"Detected Emotion: {dominant_emotion}")
                else:
                    print("No clear emotion detected.")
            except Exception as e:
                print(f"Error in emotion detection: {e}")

        cap.release()  # Release video

        print("\nSummary of Detected Emotions:")
        print(emotions_detected)

        return emotions_detected  # Return detected emotions list