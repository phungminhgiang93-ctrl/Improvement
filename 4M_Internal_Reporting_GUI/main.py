
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from pathlib import Path

from gui.app_window import AppWindow
from database import init_db

BASE_DIR = Path(__file__).resolve().parent
init_db()

if __name__ == "__main__":
    root = tk.Tk()
    AppWindow(root)
    root.mainloop()
