import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tkinter as tk
from gui import ColoringGUI

def main():
    root = tk.Tk()
    app = ColoringGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
