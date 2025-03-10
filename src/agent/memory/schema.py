from typing import TypedDict

# Define the structure using TypedDict
class Preference(TypedDict):
    outfit: str
    response: str
    emotion: str

class Context(TypedDict):
    occasion: str
    weather: str
    style: str

class Conversation(TypedDict):
    context: Context
    preferences: list[Preference]

class User(TypedDict):
    name: str
    gender: str
    height: str
    body_type: str
    conversations: list[Conversation]

# The full schema
UserSchema = dict[str, User]