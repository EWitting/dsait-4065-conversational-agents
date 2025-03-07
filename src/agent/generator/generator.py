class Generator:
    def __init__(self):
        pass

    def generate(self, context: str, memories: list[str]):
        text = self.generate_text(context, memories)
        image = self.generate_image(text)
        return text, image

    def generate_text(self, context: str, memories: list[str]) -> str:
        return "A wedding dress, sneakers, and a cowboy hat"

    def generate_image(self, description: str) -> str:
        return "<insert image of a wedding dress, sneakers, and a cowboy hat>"
