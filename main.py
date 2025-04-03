import tkinter as tk
from tkinter import messagebox
from dotenv import load_dotenv
import sys
import argparse

import sv_ttk
from src.gui.fashionAssistantGUI import FashionAssistantGUI


load_dotenv()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--disable-long-term-retrieval",
        "-d",
        action="store_true",
        help="Disable long-term retrieval for the assistant",
    )
    args = parser.parse_args()

    root = tk.Tk()

    def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            root.destroy()
            sys.exit(0)

    root.protocol("WM_DELETE_WINDOW", on_closing)
    # NOTE: does not do anything yet. Need to migrate from Tk to TTK widgets!
    sv_ttk.set_theme("dark")
    app = FashionAssistantGUI(
        root, long_term_retrieval=not args.disable_long_term_retrieval
    )
    root.mainloop()
