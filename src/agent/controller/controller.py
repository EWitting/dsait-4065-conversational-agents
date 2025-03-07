from dataclasses import dataclass, field
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
    memory: Memory = field(default_factory=Memory)
    emotion: EmotionSystem = field(default_factory=EmotionSystem)
    asr: ASR = field(default_factory=ASR)
    generator: Generator = field(default_factory=Generator)

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
        # returns text and emotion
        return input("Type your response: "), input("Type your emotion: ")
