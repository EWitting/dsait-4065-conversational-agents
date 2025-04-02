from dataclasses import dataclass, field
from enum import Enum
from src.agent.memory.memory import Memory
from src.agent.emotion.emotion import EmotionSystem
from src.agent.asr.asr import ASR
from time import sleep
from src.agent.generator.generator import Generator
import sounddevice as sd
import wavio
import uuid
import os
from ..memory.schema import Context, User, Preference

import re


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
    memory: Memory = field(default_factory=Memory)
    emotion: EmotionSystem = field(default_factory=EmotionSystem)
    asr: ASR = field(default_factory=ASR)
    generator: Generator = field(default_factory=Generator)

    user: str = ""
    user_attributes: dict = None
    conversation_index: int = 0
    context: Context = None

    phase: ConversationPhase = ConversationPhase.ASK_NAME

    def start(self):
        while not self.phase == ConversationPhase.END:
            self.step()
            sleep(0.1)

    def step(self) -> str:
        match self.phase:
            case ConversationPhase.ASK_NAME:
                self.phase = self.handle_ask_name()
            case ConversationPhase.ASK_CONTEXT:
                self.phase = self.handle_ask_context()
            case ConversationPhase.RECOMMENDING:
                self.phase = self.handle_recommending()

    def handle_ask_name(self) -> ConversationPhase:
        # Assume that it will be allways the same user
        users = self.memory.list_users()
        if len(users) > 0:
            self.user = users[0]["name"]
            self.user_attributes = {
                k: v for k, v in users[0].items() if k not in ["conversations", "name"]
            }
            self.speak(f"Welcome back {self.user}!")
            return ConversationPhase.ASK_CONTEXT

        self.speak("Hi! I'm an AI fashion assistant. What's your name?")
        response, _ = self.listen()
        self.user = response

        self.speak(
            f"Hi {self.user}, let's start with some personal questions to give you better recommendations."
        )

        self.speak("What gender best describes your clothing preferences?")
        gender, _ = self.listen()

        self.speak("What is your height?")
        height, _ = self.listen()

        self.speak("What is your body type?")
        body_type, _ = self.listen()

        user = dict(
            name=self.user,
            gender=gender,
            height=height,
            body_type=body_type,
            conversations=[],
        )
        self.memory.create_user(user)
        self.user_attributes = {
            k: v for k, v in user.items() if k not in ["conversations", "name"]
        }
        self.speak("Thank you for providing this information, I will remember it.")

        return ConversationPhase.ASK_CONTEXT

    def handle_ask_context(self) -> ConversationPhase:
        self.speak("What's the occasion today?")
        occasion, _ = self.listen()

        self.speak("And what's the weather like?")
        weather, _ = self.listen()

        self.speak("What style are you looking for?")
        style, _ = self.listen()

        context = dict(occasion=occasion, weather=weather, style=style)

        self.context = context
        self.conversation_index = self.memory.create_conversation(self.user, context)
        return ConversationPhase.RECOMMENDING

    def handle_recommending(self) -> ConversationPhase:
        self.speak("Here is a recommendation for you.")
        memories = self.memory.retrieve(self.user, self.conversation_index)
        text, image = self.generator.generate(
            self.context, self.user_attributes, memories
        )
        self.speak(text)
        self.show_image(image)

        self.speak("What do you think?")
        response, emotion = self.listen()

        preference = dict(outfit=text, response=response, emotion=emotion)
        self.memory.add_preference(self.user, self.conversation_index, preference)

        self.speak("Are you satisfied with the recommendation?")
        response, _ = self.listen()

        if response.lower() == "yes":
            self.speak("Thank you for using our service. Have a nice day!")
            return ConversationPhase.END
        else:
            return ConversationPhase.RECOMMENDING

    def show_image(self, image: str):
        print(image)

    def speak(self, message: str):
        print(message)

    def listen(self) -> tuple[str, str]:
        duration = 5
        fs = 16000
        print("Listening... Please speak now.")
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
        sd.wait()
        temp_filename = f"temp/{uuid.uuid4()}.wav"
        wavio.write(temp_filename, recording, fs, sampwidth=2)

        text = self.asr.transcribe(recording)

        # Clean up the temporary file.
        os.remove(temp_filename)

        return text, "neutral"
