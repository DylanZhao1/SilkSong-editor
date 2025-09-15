import customtkinter as ctk
from modules.modern_editor_ui import ModernEditorUI

def main():
    """
    现代化主程序入口
    """
    # 创建CustomTkinter根窗口
    root = ctk.CTk()
    
    # 设置窗口图标（如果有的话）
    try:
        root.iconbitmap("icon.ico")  # 可选：添加图标
    except:
        pass  # 如果没有图标文件就忽略
    
    # 创建现代化UI应用
    app = ModernEditorUI(root)
    
    # 启动主循环
    root.mainloop()

if __name__ == '__main__':
    main()