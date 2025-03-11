from dataclasses import dataclass, field
from enum import Enum
from src.agent.memory.memory import Memory
from src.agent.emotion.linguistic import LinguisticSystem
from src.agent.asr.asr import ASR
from time import sleep
from src.agent.generator.generator import Generator
import sounddevice as sd
import wavio
import uuid
import os
from ..memory.schema import Context, User, Preference
import re

os.environ['TOKENIZERS_PARALLELISM'] = "true"

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
    emotion: LinguisticSystem = field(default_factory=LinguisticSystem)
    asr: ASR = field(default_factory=ASR)
    generator: Generator = field(default_factory=Generator)

    user: str = ""
    conversation_index: int = 0
    context: Context = None
    user_info = None
    
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
        self.speak("Hi! I'm an AI fashion assistant. What's your name?")
        response, _ = self.listen(prompt = "Hi! I'm an AI fashion assistant. What's your name?")
        self.user = response

        # Check if the user already exists in the database
        if self.memory.user_exists(self.user):
            self.speak("Hi again")
            return ConversationPhase.ASK_CONTEXT
        
        self.speak(f"Hi {self.user}, let's start with some personal questions to give you better recommendations.")

        self.speak("What gender best describes your clothing preferences?")
        gender, _ = self.listen(prompt = "What gender best describes your clothing preferences?")
        
        self.speak("What is your height?")
        height, _ = self.listen(prompt = "What is your height?")

        self.speak("What is your body type?")
        body_type, _ = self.listen(prompt = "What is your body type?")

        user = dict(
            name=self.user,
            gender=gender,
            height=height,
            body_type=body_type,
            conversations=[]
        )
        self.user_info = dict(
            gender = gender,
            height = height,
            body_type = body_type
        )
        self.memory.create_user(user)
        self.speak("Thank you for providing this information, I will remember it.")

        return ConversationPhase.ASK_CONTEXT
        

    def handle_ask_context(self) -> ConversationPhase:
        self.speak("What's the occasion today?")
        occasion, _ = self.listen(prompt = "What's the occasion today?")
    
        self.speak("And what's the weather like?")
        weather, _ = self.listen(prompt = "And what's the weather like?")

        self.speak("What style are you looking for?")
        style, _ = self.listen(prompt = "What style are you looking for?")

        context = dict(
            occasion=occasion,
            weather=weather,
            style=style
        )

        self.context = context
        self.conversation_index = self.memory.create_conversation(self.user, context)
        return ConversationPhase.RECOMMENDING

    def handle_recommending(self) -> ConversationPhase:
        self.speak("Here is a recommendation for you.")
        memories = self.memory.retrieve(self.user, self.conversation_index)
        context_and_user_info = self.context | self.user_info
        text, image = self.generator.generate(context_and_user_info, memories)
        self.speak(text)
        self.show_image(image)

        self.speak("What do you think?")
        response, emotion = self.listen(prompt = "What do you think?")
    
        preference = dict(
            outfit=text,
            response=response,
            emotion=emotion
        )
        self.memory.add_preference(self.user, self.conversation_index, preference)

        self.speak("Are you satisfied with the recommendation?")
        response, _ = self.listen(prompt = "Are you satisfied with the recommendation?")

        if "yes" in response.lower():
            self.speak("Thank you for using our service. Have a nice day!")
            return ConversationPhase.ASK_NAME
        else:
            return ConversationPhase.RECOMMENDING

    def show_image(self, image):
        image.show()

    def speak(self, message: str):
        print(message)

    def listen(self, prompt: str) -> tuple[str,str]:
        duration = 5 
        fs = 16000 
        print("Listening... Please speak now.")
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
        sd.wait()
        temp_filename = f"temp_{uuid.uuid4()}.wav"
        wavio.write(temp_filename, recording, fs, sampwidth=2)
        
        text = self.asr.transcribe(prompt, temp_filename)
        emotion = self.emotion.get_emotion(text)
        
        # Clean up the temporary file.
        os.remove(temp_filename)
        print("AI heard:", text)
        print("Emotion:", emotion)
        return text, emotion