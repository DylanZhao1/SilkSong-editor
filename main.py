import tkinter as tk
from modules.editor_ui import EditorUI

def main():
    """
    主程序入口
    """
    root = tk.Tk()
    app = EditorUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()