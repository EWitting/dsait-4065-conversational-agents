class Generator:
    def __init__(self):
        pass

    def generate(self, context: str, memories: list[str]):
        text = self.generate_text(context, memories)
        image = self.generate_image(text)
        return text, image

    def generate_text(self, context: str, memories: list[str]) -> str:
        pass

    def generate_image(self, description: str) -> str:
        pass
