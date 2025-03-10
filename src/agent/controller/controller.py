from dataclasses import dataclass
from enum import Enum

import cv2

# from ..memory.memory import Memory
# from ..emotion.emotion import EmotionSystem
from src.agent.asr.asr import ASR
from time import sleep
# from ..generator.generator import Generator
import sounddevice as sd
import wavio
import uuid
import os

import re

from src.agent.emotion.emotion import EmotionSystem


def extract_name(text: str) -> str:
    """
    Extracts the name from a string like "my name is [name]."

    Args:
        text (str): The input text.

    Returns:
        str: The extracted name or an empty string if not found.
    """
    # This regex matches "my name is" (case-insensitive) followed by a sequence of letters,
    # which we'll consider the name.
    match = re.search(r"my name is\s+([\w'-]+)", text, re.IGNORECASE)
    if match:
        return match.group(1)
    return ""


class ConversationPhase(Enum):
    ASK_NAME = "ask_name"
    ASK_CONTEXT = "ask_context"
    RECOMMENDING = "recommending"
    END = "end"


@dataclass
class Controller:
    # memory: Memory
    emotion: EmotionSystem
    asr: ASR
    # generator: Generator

    user: str = ""
    context: str = ""

    is_finished: bool = False
    phase: ConversationPhase = ConversationPhase.ASK_NAME

    def __init__(self, asr: ASR, emotion: EmotionSystem):
        # self.memory = memory
        self.emotion = emotion
        self.asr = asr
        # self.generator = generator
        self.user = ""
        self.context = ""
        self.is_finished = False
        self.phase = ConversationPhase.ASK_NAME

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
        response = self.listen()
        self.user = response
        # test
        name = extract_name(response)
        print(response, name)
        self.speak(name)
        # self.memory.add_user(self.user)
        self.phase = ConversationPhase.ASK_CONTEXT

    def handle_ask_context(self):
        self.speak("What's the occasion?")
        response = self.listen()
        self.context = response
        # self.memory.add_context(self.user, self.context)
        self.phase = ConversationPhase.RECOMMENDING

    def handle_recommending(self):
        self.speak("Here is a recommendation for you.")
        # text, image = self.generator.generate(self.context, self.memory.get_memories(self.user))
        text = "A 3-piece navy suit with a black tie, black shoes and a shiny black belt!"
        self.speak(text)
        # self.show_image(image)
        response = self.listen()
        preference = text + "response: " + response
        # self.memory.add_memory(self.user, preference)
        self.phase = ConversationPhase.ASK_NAME

        self.speak("Are you satisfied with the recommendation?")
        response = self.listen()
        if response == "yes":
            self.phase = ConversationPhase.END
            self.is_finished = True
            self.speak("Thank you for using our service. Have a nice day!")
        else:
            self.phase = ConversationPhase.ASK_NAME

    def show_image(self, image: str):
        pass

    def speak(self, message: str):
        # For now, simply print the message.
        print("AI says:", message)

    def listen(self) -> tuple[str, str]:
        duration = 5
        fs = 16000
        temp_audio_file = f"temp_audio_{uuid.uuid4()}.wav"
        temp_video_file = f"temp_video_{uuid.uuid4()}.avi"

        print("Recording audio...")
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)

        print("Recording video...")
        cap = cv2.VideoCapture(0)  # Open the default camera
        if not cap.isOpened():
            self.speak("Error: Unable to access the camera.")
            return "", ""

        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        out = cv2.VideoWriter(temp_video_file, fourcc, 20.0, (640, 480))

        for _ in range(int(duration * 20)):  # Assuming 20 FPS for 5 seconds
            ret, frame = cap.read()
            if ret:
                out.write(frame)


        sd.wait()

        cap.release()
        out.release()

        sleep(1)

        print("Video recording complete.")

        wavio.write(temp_audio_file, recording, fs, sampwidth=2)
        print("Audio recording complete.")

        text = self.asr.transcribe(temp_audio_file)
        emotion = self.emotion.get_emotion(temp_video_file, temp_audio_file)

        return text, emotion


if __name__ == "__main__":
    from src.agent.asr.asr import ASR
    from src.agent.emotion.emotion import EmotionSystem


    asr_instance = ASR(model_name="base")
    emotion = EmotionSystem()


    emotion_system = EmotionSystem()


    controller = Controller(asr=asr_instance, emotion=emotion_system)


    print("Starting the listen method test...\n")
    text, emotion = controller.listen()


    print(f"Transcribed Text: {text}")
    print(f"Detected Emotion: {emotion}")


