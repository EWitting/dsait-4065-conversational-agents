from dataclasses import dataclass
from enum import Enum
#from ..memory.memory import Memory
#from ..emotion.emotion import EmotionSystem
from src.agent.asr.asr import ASR
from time import sleep
#from ..generator.generator import Generator
import sounddevice as sd
import wavio
import uuid
import os

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
    #memory: Memory
    #emotion: EmotionSystem
    asr: ASR
    #generator: Generator

    user: str = ""
    context: str = ""
    
    is_finished: bool = False
    phase: ConversationPhase = ConversationPhase.ASK_NAME

    def __init__(self, asr: ASR):
        #self.memory = memory
        #self.emotion = emotion
        self.asr = asr
        #self.generator = generator
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
        #test
        name = extract_name(response)
        print(response, name)
        self.speak(name)
        #self.memory.add_user(self.user)
        self.phase = ConversationPhase.ASK_CONTEXT

    def handle_ask_context(self):
        self.speak("What's the occasion?")
        response = self.listen()
        self.context = response
        #self.memory.add_context(self.user, self.context)
        self.phase = ConversationPhase.RECOMMENDING

    def handle_recommending(self):
        self.speak("Here is a recommendation for you.")
        #text, image = self.generator.generate(self.context, self.memory.get_memories(self.user))
        text = "A 3-piece navy suit with a black tie, black shoes and a shiny black belt!"
        self.speak(text)
        #self.show_image(image)
        response = self.listen()
        preference = text + "response: " + response
        #self.memory.add_memory(self.user, preference)
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

    def listen(self) -> str:
        duration = 5 
        fs = 16000 
        print("Listening... Please speak now.")
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
        sd.wait()
        temp_filename = f"temp_{uuid.uuid4()}.wav"
        wavio.write(temp_filename, recording, fs, sampwidth=2)
        
        text = self.asr.transcribe(temp_filename)
        
        # Clean up the temporary file.
        os.remove(temp_filename)
        
        return text
if __name__ == "__main__":
    from src.agent.asr.asr import ASR
    asr_instance = ASR(model_name="base")
    controller = Controller(asr=asr_instance)
    controller.start()