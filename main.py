import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from interface import SongFinderUI
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    app = SongFinderUI(root)
    root.mainloop()