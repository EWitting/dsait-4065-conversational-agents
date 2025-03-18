import tkinter as tk
from tkinter import messagebox
from tkinter import messagebox
from dotenv import load_dotenv
import sys
from src.gui.fashionAssistantGUI import FashionAssistantGUI


load_dotenv()

if __name__ == "__main__":
    root = tk.Tk()

    def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            root.destroy()
            sys.exit(0)

    root.protocol("WM_DELETE_WINDOW", on_closing)
    app = FashionAssistantGUI(root)
    root.mainloop()
