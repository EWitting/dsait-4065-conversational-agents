from dataclasses import dataclass, field
from enum import Enum
#from ..memory.memory import Memory
#from ..emotion.emotion import EmotionSystem
from src.agent.emotion.emotion import EmotionSystem
from src.agent.asr import asr

#from ..asr.asr import ASR
from time import sleep
#from ..generator.generator import Generator
import cv2
import sounddevice as sd
from scipy.io.wavfile import write
import threading
import time
import numpy as np
import os


os.environ["TOKENIZERS_PARALLELISM"] = "false"


class ConversationPhase(Enum):
    ASK_NAME = "ask_name"
    ASK_CONTEXT = "ask_context"
    RECOMMENDING = "recommending"
    END = "end"


@dataclass
class Controller:
    #memory: Memory = field(default_factory=Memory)
    emotion: EmotionSystem = field(default_factory=EmotionSystem)
    asr: asr = field(default_factory=asr)
    #generator: Generator = field(default_factory=Generator)

    user: str = ""
    context: str = ""

    is_finished: bool = False
    phase: ConversationPhase = ConversationPhase.ASK_NAME

    def start(self):
        while not self.is_finished:
            self.step()
            sleep(0.1)

    def step(self) -> str:
        match self.phase:
            case ConversationPhase.ASK_NAME:
                self.handle_ask_name()
            case ConversationPhase.ASK_CONTEXT:
                self.handle_ask_context()
            case ConversationPhase.RECOMMENDING:
                self.handle_recommending()

    def handle_ask_name(self):
        self.speak("Hi! I'm an AI fashion assistant. What's your name?")
        response, _ = self.listen()
        self.user = response
        self.memory.add_user(self.user)
        self.phase = ConversationPhase.ASK_CONTEXT

    def handle_ask_context(self):
        self.speak("What's the occasion?")
        response = self.listen()
        self.context = response
        self.memory.add_context(self.user, self.context)
        self.phase = ConversationPhase.RECOMMENDING

    def handle_recommending(self):
        self.speak("Here is a recommendation for you.")
        memories = self.memory.retrieve(self.user, self.context)
        text, image = self.generator.generate(self.context, memories)
        self.speak(text)
        self.show_image(image)
        self.speak("What do you think?")
        response, emotion = self.listen()
        preference = f"{text}, response: {response}, emotion: {emotion}"
        self.memory.add_memory(self.user, self.context, preference)

        self.speak("Are you satisfied with the recommendation?")
        response, _ = self.listen()
        if response == "yes":
            self.phase = ConversationPhase.END
            self.is_finished = True
            self.speak("Thank you for using our service. Have a nice day!")
        else:
            # Loop will continue recommendation process
            pass

    def show_image(self, image: str):
        print(image)

    def speak(self, message: str):
        print(message)

    def listen(self) -> tuple[str, str]:
            video_file = "recorded_video.avi"
            audio_file = "recorded_audio.wav"

            video_thread = threading.Thread(target=self.record_video, args=(video_file,))
            audio_thread = threading.Thread(target=self.record_audio, args=(audio_file,))
            video_thread.start()
            audio_thread.start()

            video_thread.join()
            audio_thread.join()


            time.sleep(1)
            response = self.asr.transcribe(audio_file)
            emotion = self.emotion.get_emotion(video_file, audio_file)

            return response, emotion

    def record_video(self, filename):
        print("Starting video recording...")
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open webcam.")
            return

        fourcc = cv2.VideoWriter_fourcc(*'MJPG')  t
        out = cv2.VideoWriter(filename, fourcc, 20.0, (640, 480))

        if not out.isOpened():
            print("Error: Could not open video file for writing.")
            return

        start_time = time.time()
        frame_count = 0

        while time.time() - start_time < 5:  # Record for 5 seconds
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to grab frame.")
                break
            out.write(frame)
            frame_count += 1

        cap.release()
        out.release()
        print(f"Video saved as {filename} with {frame_count} frames.")

    def record_audio(self, filename):
            duration = 5
            sample_rate = 44100

            print("Recording audio...")
            audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype=np.int16)
            sd.wait()
            print("Audio recording complete.")

            write(filename, sample_rate, audio_data)


if __name__ == "__main__":
    from src.agent.asr.asr import ASR
    from src.agent.emotion.emotion import EmotionSystem


    asr_instance = ASR(model_name="base")
    emotion_instance = EmotionSystem()

    controller = Controller(asr=asr_instance, emotion=emotion_instance)

    print("Starting video and audio recording for emotion detection...")
    response, emotion = controller.listen()

    print("User response (ASR transcription):", response)
    print("Detected Emotion:", emotion)

    print("Audio file recorded as 'recorded_audio.wav'")



    detected_emotion = emotion_instance.get_emotion("recorded_video.avi", "recorded_audio.wav") # Pass the recorded files for emotion detection
    print("Detected Emotion from Video and Audio (direct test):", detected_emotion)


