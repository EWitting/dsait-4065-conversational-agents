from dataclasses import dataclass, field

@dataclass
class Memory:
    # User -> Context -> Response
    data: dict[str, dict[str, list[str]]] = field(default_factory=dict)

    def retrieve(self, user, context) -> str:
        return self.data[user][context]

    def add_user(self, user):   
        self.data[user] = {}

    def add_context(self, user, context):
        self.data[user][context] = []

    def add_memory(self, user, context, response):
        self.data[user][context].append(response)

