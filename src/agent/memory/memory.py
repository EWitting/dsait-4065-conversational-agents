from dataclasses import dataclass, field
from .schema import UserSchema, Preference, Context, Conversation, User
from .retrieval import retrieve
@dataclass
class Memory:
    data: UserSchema = field(default_factory=dict)
    
    def user_exists(self, user) -> bool:
        return user in self.data

    def create_user(self, user) -> None:   
        self.data[user['name']] = user

    def create_conversation(self, user, context) -> int:        
        conversation = dict(    
            context=context,
            preferences=[]
        )
        self.data[user]["conversations"].append(conversation)
        return len(self.data[user]["conversations"]) - 1 # index of the conversation    

    def add_preference(self, user, conversation_index, preference) -> None:
        self.data[user]["conversations"][conversation_index]["preferences"].append(preference)

    def retrieve(self, user, conversation_index) -> list[str]:

        conversations = self.data[user]["conversations"]
        selection = retrieve(conversations, conversation_index)
        
        # Convert each preference entry to a single string
        return list(map(lambda p: self._preference_text_format(p), selection))

    # TODO: this formatting for the prompt should probably be part of the generation code
    def _preference_text_format(self, preference):
        return f"Of the outfit '{preference['outfit']}', the user thinks: {preference['response']}, it makes them feel {preference['emotion']}"

        