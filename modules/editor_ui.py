import tkinter as tk
from tkinter import ttk, messagebox
import os
from .file_utils import FileUtils

class EditorUI:
    def __init__(self, root):
        """
        初始化编辑器UI
        
        参数:
            root: Tkinter根窗口
        """
        self.root = root
        self.root.title('Silk 存档编辑器')
        self.root.geometry('800x600')
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # 数据相关变量
        self.data = None
        self.file_path = None
        self.modified = False
        
        # 状态栏变量
        self.status_var = tk.StringVar()
        self.status_var.set('就绪')
        
        # 创建文件工具类
        self.file_utils = FileUtils(self.update_status)
        
        # 创建UI组件
        self._create_menu()
        self._create_main_frame()
        self._create_status_bar()
    
    def _create_menu(self):
        """
        创建菜单栏
        """
        menubar = tk.Menu(self.root)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="打开...", command=self.load_file)
        file_menu.add_command(label="保存", command=self.save_file)
        file_menu.add_command(label="另存为游戏存档...", command=self.save_as_game_file)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.on_close)
        menubar.add_cascade(label="文件", menu=file_menu)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="关于", command=self.show_about)
        menubar.add_cascade(label="帮助", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def _create_main_frame(self):
        """
        创建主框架
        """
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建左侧树形视图
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 树形视图
        self.tree = ttk.Treeview(tree_frame, columns=('value',))
        self.tree.heading('#0', text='路径')
        self.tree.heading('value', text='值')
        self.tree.column('value', width=200)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 绑定选择事件
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        
        # 创建右侧值编辑框架
        edit_frame = ttk.LabelFrame(main_frame, text='编辑值')
        edit_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
        
        # 值输入框
        self.value_entry = ttk.Entry(edit_frame, width=30)
        self.value_entry.pack(padx=10, pady=10)
        
        # 更新按钮
        update_button = ttk.Button(edit_frame, text='更新', command=self.update_value)
        update_button.pack(padx=10, pady=10)
    
    def _create_status_bar(self):
        """
        创建状态栏
        """
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def update_status(self, message):
        """
        更新状态栏信息
        
        参数:
            message: 状态信息
        """
        self.status_var.set(message)
    
    def on_close(self):
        """
        关闭窗口前检查是否有未保存的修改
        """
        if self.modified:
            if messagebox.askyesno('确认', '有未保存的修改，是否保存？'):
                self.save_file()
        
        self.root.destroy()
    
    def load_file(self):
        """
        加载文件
        """
        # 如果有未保存的修改，提示保存
        if self.modified:
            if messagebox.askyesno('确认', '有未保存的修改，是否保存？'):
                self.save_file()
        
        # 加载新文件
        data, file_path = self.file_utils.load_file()
        if data and file_path:
            self.data = data
            self.file_path = file_path
            self.modified = False
            
            # 清空树形视图
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # 填充树形视图
            self.populate_tree('', self.data)
    
    def save_file(self):
        """
        保存文件
        """
        if self.file_utils.save_file(self.data, self.file_path):
            self.modified = False
    
    def save_as_game_file(self):
        """
        将数据保存为游戏可读取的.dat文件
        """
        self.file_utils.save_as_game_file(self.data)
    
    def show_about(self):
        """
        显示关于信息
        """
        messagebox.showinfo('关于', 'Silk 存档编辑器\n版本: 1.0\n\n一个简单的游戏存档编辑工具')
    
    def populate_tree(self, parent, data, key=''):
        """
        填充树形视图
        
        参数:
            parent: 父节点ID
            data: 要填充的数据
            key: 节点键名
        """
        if isinstance(data, dict):
            # 字典
            node = self.tree.insert(parent, 'end', text=key, values=())
            for k, v in data.items():
                self.populate_tree(node, v, k)
        elif isinstance(data, list):
            # 列表
            node = self.tree.insert(parent, 'end', text=f"{key} [列表]", values=())
            for i, item in enumerate(data):
                self.populate_tree(node, item, str(i))
        else:
            # 叶子节点
            self.tree.insert(parent, 'end', text=key, values=(str(data),))
    
    def get_full_path(self, item):
        """
        获取节点的完整路径
        
        参数:
            item: 节点ID
            
        返回:
            list: 路径列表
        """
        path = []
        while item != '':
            path.insert(0, self.tree.item(item, 'text'))
            item = self.tree.parent(item)
        # 移除根节点
        if path and path[0] == '':
            path.pop(0)
        return path

    def get_value_from_path(self, data, path):
        """
        根据路径获取值
        
        参数:
            data: 数据
            path: 路径列表
            
        返回:
            任意类型: 路径对应的值
        """
        current = data
        for key in path:
            if key.endswith(' [列表]'):
                key = key[:-6]
            if isinstance(current, dict):
                if key not in current:
                    return None
                current = current[key]
            elif isinstance(current, list):
                try:
                    idx = int(key)
                    if idx >= len(current):
                        return None
                    current = current[idx]
                except (ValueError, IndexError):
                    return None
            else:
                return None
        return current

    def set_value_from_path(self, data, path, value):
        """
        根据路径设置值
        
        参数:
            data: 数据
            path: 路径列表
            value: 新值
            
        返回:
            bool: 是否设置成功
        """
        if not data or not path:
            messagebox.showerror('错误', '数据或路径为空')
            return False
        
        # 特殊处理playerData下的字段 - 直接访问
        if len(path) >= 2 and path[0] == 'playerData':
            field_name = path[1]
            if isinstance(data, dict) and 'playerData' in data and isinstance(data['playerData'], dict):
                if field_name in data['playerData']:
                    original_value = data['playerData'][field_name]
                    
                    # 根据原始值类型进行转换
                    try:
                        if isinstance(original_value, bool):
                            if value.lower() in ('true', 'false'):
                                data['playerData'][field_name] = value.lower() == 'true'
                            else:
                                messagebox.showerror('错误', f'布尔值必须是 "true" 或 "false"')
                                return False
                        elif isinstance(original_value, int):
                            # 支持小数点输入，但转换为整数
                            data['playerData'][field_name] = int(float(value))
                        elif isinstance(original_value, float):
                            data['playerData'][field_name] = float(value)
                        else:
                            # 字符串或其他类型
                            data['playerData'][field_name] = value
                            
                        return True
                    except ValueError:
                        messagebox.showerror('错误', f'无法将 "{value}" 转换为正确的类型')
                        return False
        
        # 处理一般情况
        current = data
        path_copy = path.copy()  # 创建路径的副本，避免修改原始路径
        
        # 处理最后一个键之前的路径
        while len(path_copy) > 1:
            key = path_copy.pop(0)
            
            if key.endswith(' [列表]'):
                key = key[:-6]
                
            if isinstance(current, dict):
                if key not in current:
                    messagebox.showerror('错误', f'路径中的键 "{key}" 不存在')
                    return False
                current = current[key]
            elif isinstance(current, list):
                try:
                    idx = int(key)
                    if idx >= len(current):
                        messagebox.showerror('错误', f'列表索引 {idx} 超出范围')
                        return False
                    current = current[idx]
                except ValueError:
                    messagebox.showerror('错误', f'无效的列表索引: "{key}"')
                    return False
            else:
                messagebox.showerror('错误', f'路径中的 "{key}" 不是容器类型')
                return False
        
        # 处理最后一个键
        last_key = path_copy[0]
        
        if last_key.endswith(' [列表]'):
            last_key = last_key[:-6]
        
        # 更新值
        try:
            if isinstance(current, dict):
                if last_key not in current:
                    messagebox.showerror('错误', f'键 "{last_key}" 不存在')
                    return False
                
                original_value = current[last_key]
                
                # 根据原始值类型进行转换
                if isinstance(original_value, bool):
                    if value.lower() in ('true', 'false'):
                        current[last_key] = value.lower() == 'true'
                    else:
                        messagebox.showerror('错误', f'布尔值必须是 "true" 或 "false"')
                        return False
                elif isinstance(original_value, int):
                    try:
                        # 支持小数点输入，但转换为整数
                        current[last_key] = int(float(value))
                    except ValueError:
                        messagebox.showerror('错误', f'无法将 "{value}" 转换为整数')
                        return False
                elif isinstance(original_value, float):
                    try:
                        current[last_key] = float(value)
                    except ValueError:
                        messagebox.showerror('错误', f'无法将 "{value}" 转换为浮点数')
                        return False
                else:
                    # 字符串或其他类型
                    current[last_key] = value
                    
            elif isinstance(current, list):
                try:
                    idx = int(last_key)
                    if idx >= len(current):
                        messagebox.showerror('错误', f'列表索引 {idx} 超出范围')
                        return False
                        
                    original_value = current[idx]
                    
                    # 根据原始值类型进行转换
                    if isinstance(original_value, bool):
                        if value.lower() in ('true', 'false'):
                            current[idx] = value.lower() == 'true'
                        else:
                            messagebox.showerror('错误', f'布尔值必须是 "true" 或 "false"')
                            return False
                    elif isinstance(original_value, int):
                        try:
                            # 支持小数点输入，但转换为整数
                            current[idx] = int(float(value))
                        except ValueError:
                            messagebox.showerror('错误', f'无法将 "{value}" 转换为整数')
                            return False
                    elif isinstance(original_value, float):
                        try:
                            current[idx] = float(value)
                        except ValueError:
                            messagebox.showerror('错误', f'无法将 "{value}" 转换为浮点数')
                            return False
                    else:
                        # 字符串或其他类型
                        current[idx] = value
                except ValueError:
                    messagebox.showerror('错误', f'无效的列表索引: "{last_key}"')
                    return False
            else:
                messagebox.showerror('错误', f'无法更新非容器类型')
                return False
                
            return True
        except Exception as e:
            messagebox.showerror('错误', f'更新值时出错: {str(e)}')
            return False

    def on_select(self, event):
        """
        树形视图选择事件处理
        
        参数:
            event: 事件对象
        """
        selected = self.tree.selection()
        if not selected:
            return

        item = selected[0]
        values = self.tree.item(item, 'values')
        if values:  # 只有叶子节点有值
            self.value_entry.delete(0, tk.END)
            self.value_entry.insert(0, values[0])

    def update_value(self):
        """
        更新选中节点的值
        """
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning('警告', '请先选择一个项目')
            return

        item = selected[0]
        if not self.tree.item(item, 'values'):  # 不是叶子节点
            messagebox.showwarning('警告', '只能修改叶子节点的值')
            return

        new_value = self.value_entry.get().strip()
        if not new_value:
            messagebox.showwarning('警告', '请输入新的值')
            return

        path = self.get_full_path(item)
                    
        # 使用set_value_from_path更新值
        if self.set_value_from_path(self.data, path, new_value):
            # 更新树形视图
            # 获取更新后的值
            updated_value = self.get_value_from_path(self.data, path)
            if updated_value is not None:
                self.tree.set(item, 'value', str(updated_value))
                self.modified = True
                messagebox.showinfo('成功', f'值已更新为: {updated_value}')
            else:
                messagebox.showerror('错误', '无法获取更新后的值')
        else:
            messagebox.showerror('错误', '更新值失败')