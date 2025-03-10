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

        frame_count = 0  # To control how often we analyze the frames
        analyze_every = 5  # Analyze every 5th frame for performance optimization

        while True:
            ret, frame = video_capture.read()
            if not ret:
                break

            frame_count += 1

            # Process every 'analyze_every' frame to improve performance
            if frame_count % analyze_every == 0:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

                """
                if len(faces) == 0:
                    print("No face detected in frame.")
                else:
                    print(f"Detected {len(faces)} faces.")
                    """

                for (x, y, w, h) in faces:
                    face = frame[y:y + h, x:x + w]

                    try:
                        # Save the frame as an image for debugging purposes
                        cv2.imwrite("frame.jpg", frame)  # Save the current frame as 'frame.jpg'
                        #print("Frame saved for emotion analysis")

                        # Analyze the saved frame using DeepFace
                        analysis = DeepFace.analyze("frame.jpg", actions=['emotion'])
                        #print("DeepFace Analysis Result:", analysis)  # Debugging line

                        emotion = analysis[0]['dominant_emotion']
                        emotions_detected.append(emotion)
                    except Exception as e:
                        print(f"Error analyzing face: {e}")
                        emotions_detected.append("neutral")  # In case of error, add neutral

        video_capture.release()

        most_common_emotion = " "
        if emotions_detected:
            most_common_emotion = Counter(emotions_detected).most_common(1)[0][0]

        return most_common_emotion
if __name__ == "__main__":
    audio = "/Users/shivangikachole/PycharmProjects/dsait-4065-conversational-agents/src/agent/emotion/test.mov"
    video_system = VideoSystem()
    detected_emotion = video_system.get_emotion(audio)

    print("Detected Emotion:", detected_emotion)