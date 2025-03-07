from dataclasses import dataclass
from enum import Enum
from ..memory.memory import Memory
from ..emotion.emotion import EmotionSystem
from ..asr.asr import ASR
from time import sleep
from ..generator.generator import Generator

class ConversationPhase(Enum):
    ASK_NAME = "ask_name"
    ASK_CONTEXT = "ask_context"
    RECOMMENDING = "recommending"
    END = "end"

@dataclass
class Controller:
    memory: Memory
    emotion: EmotionSystem
    asr: ASR
    generator: Generator

    user: str = ""
    context: str = ""
    
    is_finished: bool = False
    phase: ConversationPhase = ConversationPhase.GREETING

    def __init__(self):
        pass

    def start(self):
        while not self.finished:
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
        response, emotion = self.listen()
        preference = f"{text}, response: {response}, emotion: {emotion}"
        self.memory.add_memory(self.user, preference)
        self.phase = ConversationPhase.ASK_NAME

        self.speak("Are you satisfied with the recommendation?")
        response = self.listen()
        if response == "yes":
            self.phase = ConversationPhase.END
            self.is_finished = True
            self.speak("Thank you for using our service. Have a nice day!")
        else:
            # Loop will continue recommendation process
            pass

    def show_image(self, image: str):
        pass

    def speak(self, message: str):
        pass

    def listen(self) -> str, str:
        # returns text and emotion
        pass
