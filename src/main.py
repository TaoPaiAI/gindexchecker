import tkinter as tk
from gindexchecker_app import GIndexCheckerApp
from utils import resource_path, set_app_icon

if __name__ == "__main__":
    root = tk.Tk()
    set_app_icon(root)
    app = GIndexCheckerApp(root)
    root.mainloop()