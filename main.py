import tkinter as tk

from src.gui.fashionAssistantGUI import FashionAssistantGUI

if __name__ == "__main__":
    root = tk.Tk()
    app = FashionAssistantGUI(root)
    root.mainloop()