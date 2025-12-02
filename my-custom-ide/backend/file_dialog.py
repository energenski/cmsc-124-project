import tkinter as tk
from tkinter import filedialog
import sys

def open_file():
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        file_path = filedialog.askopenfilename(
            title="Open LOLCODE File",
            filetypes=[("LOLCODE Files", "*.lol"), ("All Files", "*.*")]
        )
        root.destroy()
        # Print the path to stdout so the caller can capture it
        print(file_path)
    except Exception as e:
        # Print error to stderr
        print(str(e), file=sys.stderr)

if __name__ == "__main__":
    open_file()
