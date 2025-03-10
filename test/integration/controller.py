"""Mock user input to quickly simulate multiple rounds of conversation"""

import sys
import os

# Add the src directory to the system path, very hacky but it works for easy debugging
import_path = os.path.join(os.path.dirname(__file__), '../../src')
sys.path.append(import_path)

from dataclasses import dataclass, field
from agent.controller.controller import Controller

@dataclass
class MockController(Controller):
    
    sequence: list[tuple[str, str]] = field(default_factory=list)

    def listen(self):
        if self.sequence:
            response, emotion = self.sequence.pop(0)
            print(f"> {response} ({emotion})")
            return response, emotion
        else:
            raise ValueError("No more input")

def test_one_conversation():
    sequence = [
        # New user
        ("John", "happy"),
        ("Male", "happy"),
        ("175", "happy"),
        ("Tetrahedron", "happy"),

        # Context
        ("Party", "happy"),
        ("Sunny", "happy"),
        ("Summer Vibes", "happy"),

        # Feedback + Satisfied?
        ("I don't like it, it should be more casual", "sad"),
        ("No", "sad"),
        ("I like it, but I'd prefer a top hat", "happy"),
        ("No", "sad"),
        ("That's amazing!", "happy"),
        ("Yes", "happy"),            
    ]

    controller = MockController(sequence=sequence)
    controller.start()

if __name__ == "__main__":
    test_one_conversation()



