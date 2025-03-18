import tkinter as tk
from dotenv import load_dotenv

from src.gui.fashionAssistantGUI import FashionAssistantGUI
load_dotenv()

if __name__ == "__main__":
    root = tk.Tk()
    app = FashionAssistantGUI(root)
    root.mainloop()