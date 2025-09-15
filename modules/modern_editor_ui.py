import customtkinter as ctk
from tkinter import messagebox, filedialog
import os
from .file_utils import FileUtils

class ModernEditorUI:
    def __init__(self, root):
        """
        初始化现代化编辑器UI
        
        参数:
            root: CustomTkinter根窗口
        """
        self.root = root
        self.root.title('丝之歌存档编辑器')
        self.root.geometry('1000x700')
        
        # 设置外观模式和主题
        ctk.set_appearance_mode("dark")  # 可选: "light", "dark", "system"
        ctk.set_default_color_theme("blue")  # 可选: "blue", "green", "dark-blue"
        
        # 数据相关变量
        self.data = None
        self.file_path = None
        self.modified = False
        
        # 状态栏变量
        self.status_text = "就绪"
        
        # 创建文件工具类
        self.file_utils = FileUtils(self.update_status)
        
        # 创建UI组件
        self._create_header()
        self._create_main_content()
        self._create_status_bar()
        
        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def _create_header(self):
        """
        创建顶部标题栏和按钮
        """
        # 顶部框架
        header_frame = ctk.CTkFrame(self.root, height=80)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        header_frame.pack_propagate(False)
        
        # 标题
        title_label = ctk.CTkLabel(
            header_frame, 
            text="🎮 Silk 存档编辑器", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="left", padx=20, pady=20)
        
        # 按钮框架
        button_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        button_frame.pack(side="right", padx=20, pady=20)
        
        # 文件操作按钮
        self.open_button = ctk.CTkButton(
            button_frame,
            text="📁 打开文件",
            command=self.load_file,
            width=120,
            height=35
        )
        self.open_button.pack(side="left", padx=5)
        
        self.save_button = ctk.CTkButton(
            button_frame,
            text="💾 保存",
            command=self.save_file,
            width=100,
            height=35,
            state="disabled"
        )
        self.save_button.pack(side="left", padx=5)
        
        self.save_as_button = ctk.CTkButton(
            button_frame,
            text="📤 另存为",
            command=self.save_as_game_file,
            width=120,
            height=35,
            state="disabled"
        )
        self.save_as_button.pack(side="left", padx=5)
        
        # 主题切换按钮
        self.theme_button = ctk.CTkButton(
            button_frame,
            text="🌙",
            command=self.toggle_theme,
            width=40,
            height=35
        )
        self.theme_button.pack(side="right", padx=5)
    
    def _create_main_content(self):
        """
        创建主要内容区域
        """
        # 主内容框架
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # 左侧数据树视图框架
        left_frame = ctk.CTkFrame(main_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(20, 10), pady=20)
        
        # 数据树标题
        tree_title = ctk.CTkLabel(
            left_frame, 
            text="📊 存档数据结构", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        tree_title.pack(pady=(20, 10))
        
        # 创建滚动框架来模拟树形视图
        self.tree_scroll_frame = ctk.CTkScrollableFrame(
            left_frame, 
            label_text="数据节点",
            width=400,
            height=400
        )
        self.tree_scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # 右侧编辑面板
        right_frame = ctk.CTkFrame(main_frame, width=350)
        right_frame.pack(side="right", fill="y", padx=(10, 20), pady=20)
        right_frame.pack_propagate(False)
        
        # 编辑面板标题
        edit_title = ctk.CTkLabel(
            right_frame, 
            text="✏️ 数值编辑器", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        edit_title.pack(pady=(20, 10))
        
        # 当前路径显示
        self.path_label = ctk.CTkLabel(
            right_frame,
            text="选择一个节点进行编辑",
            font=ctk.CTkFont(size=12),
            wraplength=300
        )
        self.path_label.pack(pady=10, padx=20)
        
        # 值编辑区域
        value_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        value_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(value_frame, text="当前值:", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        
        self.value_entry = ctk.CTkEntry(
            value_frame,
            placeholder_text="输入新值...",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.value_entry.pack(fill="x", pady=(5, 10))
        
        # 更新按钮
        self.update_button = ctk.CTkButton(
            value_frame,
            text="🔄 更新值",
            command=self.update_value,
            height=40,
            state="disabled"
        )
        self.update_button.pack(fill="x", pady=5)
        
        # 数据类型信息
        self.type_label = ctk.CTkLabel(
            right_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.type_label.pack(pady=10)
        
        # 帮助信息
        help_frame = ctk.CTkFrame(right_frame)
        help_frame.pack(fill="x", padx=20, pady=(20, 0))
        
        help_title = ctk.CTkLabel(
            help_frame,
            text="💡 使用提示",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        help_title.pack(pady=(15, 5))
        
        help_text = ctk.CTkLabel(
            help_frame,
            text="• 点击左侧节点选择要编辑的值\n• 在右侧输入框中修改值\n• 点击更新按钮保存更改\n• 记得保存文件",
            font=ctk.CTkFont(size=11),
            justify="left"
        )
        help_text.pack(pady=(0, 15), padx=15)
    
    def _create_status_bar(self):
        """
        创建状态栏
        """
        status_frame = ctk.CTkFrame(self.root, height=40)
        status_frame.pack(fill="x", padx=20, pady=(0, 20))
        status_frame.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text=self.status_text,
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="left", padx=20, pady=10)
        
        # 文件信息
        self.file_info_label = ctk.CTkLabel(
            status_frame,
            text="未打开文件",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.file_info_label.pack(side="right", padx=20, pady=10)
    
    def toggle_theme(self):
        """
        切换主题
        """
        current_mode = ctk.get_appearance_mode()
        if current_mode == "Dark":
            ctk.set_appearance_mode("light")
            self.theme_button.configure(text="☀️")
        else:
            ctk.set_appearance_mode("dark")
            self.theme_button.configure(text="🌙")
    
    def update_status(self, message):
        """
        更新状态栏信息
        
        参数:
            message: 状态消息
        """
        self.status_text = message
        if hasattr(self, 'status_label'):
            self.status_label.configure(text=message)
    
    def on_close(self):
        """
        处理窗口关闭事件
        """
        if self.modified:
            result = messagebox.askyesnocancel(
                '确认', 
                '文件已修改，是否保存？'
            )
            if result is True:
                self.save_file()
            elif result is None:
                return
        
        self.root.quit()
        self.root.destroy()
    
    def load_file(self):
        """
        加载文件
        """
        try:
            file_path = filedialog.askopenfilename(
                title="选择存档文件",
                filetypes=[
                    ("所有支持的文件", "*.dat;*.json;*.xml"),
                    ("DAT文件", "*.dat"),
                    ("JSON文件", "*.json"),
                    ("XML文件", "*.xml"),
                    ("所有文件", "*.*")
                ]
            )
            
            if file_path:
                self.update_status('正在加载文件...')
                result = self.file_utils.load_file(file_path)
                
                if result and result[0] is not None:
                    self.data = result[0]
                    self.file_path = file_path
                    self.modified = False
                    self.populate_tree_modern()
                    
                    # 启用按钮
                    self.save_button.configure(state="normal")
                    self.save_as_button.configure(state="normal")
                    
                    # 更新文件信息
                    filename = os.path.basename(file_path)
                    self.file_info_label.configure(text=f"文件: {filename}")
                    
                    self.update_status('文件加载成功')
                else:
                    self.update_status('文件加载失败')
                    
        except Exception as e:
            messagebox.showerror('错误', f'加载文件失败: {str(e)}')
            self.update_status('加载失败')
    
    def save_file(self):
        """
        保存文件
        """
        if self.file_path and self.data is not None:
            try:
                self.file_utils.save_file(self.data, self.file_path)
                self.modified = False
                self.update_status('文件保存成功')
            except Exception as e:
                messagebox.showerror('错误', f'保存文件失败: {str(e)}')
    
    def save_as_game_file(self):
        """
        另存为游戏存档文件
        """
        if self.data is not None:
            try:
                file_path = filedialog.asksaveasfilename(
                    title="另存为游戏存档",
                    defaultextension=".dat",
                    filetypes=[
                        ("DAT文件", "*.dat"),
                        ("JSON文件", "*.json"),
                        ("所有文件", "*.*")
                    ]
                )
                
                if file_path:
                    self.file_utils.save_file(self.data, file_path)
                    self.update_status('文件另存成功')
                    
            except Exception as e:
                messagebox.showerror('错误', f'另存文件失败: {str(e)}')
    
    def populate_tree_modern(self):
        """
        填充数据树
        """
        # 清空现有内容
        for widget in self.tree_scroll_frame.winfo_children():
            widget.destroy()
        
        if self.data:
            # 显示加载提示
            self.update_status('正在加载数据树...')
            # 使用after方法异步创建树节点，避免界面卡死
            self.root.after(100, lambda: self._create_tree_nodes_async(self.tree_scroll_frame, self.data, ""))
    
    def _create_tree_nodes_async(self, parent, data, path_prefix, processed_count=0, max_per_batch=20):
        """
        异步创建树节点，分批处理避免界面卡死
        """
        if isinstance(data, dict):
            items = list(data.items())
            batch_items = items[processed_count:processed_count + max_per_batch]
            
            for key, value in batch_items:
                current_path = f"{path_prefix}.{key}" if path_prefix else key
                
                if isinstance(value, (dict, list)):
                    # 创建可展开的节点
                    node_frame = ctk.CTkFrame(parent)
                    node_frame.pack(fill="x", padx=5, pady=2)
                    
                    node_button = ctk.CTkButton(
                        node_frame,
                        text=f"📁 {key}",
                        command=lambda p=current_path: self.select_node(p),
                        anchor="w",
                        fg_color="transparent",
                        text_color=("gray10", "gray90"),
                        hover_color=("gray80", "gray20")
                    )
                    node_button.pack(fill="x", padx=5, pady=2)
                    
                    # 只显示前几个子项，其余延迟加载
                    if len(str(value)) < 1000:  # 小数据直接显示
                        child_frame = ctk.CTkFrame(node_frame, fg_color="transparent")
                        child_frame.pack(fill="x", padx=20)
                        self._create_tree_nodes_simple(child_frame, value, current_path)
                    else:
                        # 大数据显示可点击的展开按钮
                        expand_button = ctk.CTkButton(
                            node_frame,
                            text="📂 点击展开查看内容...",
                            command=lambda p=current_path, v=value, nf=node_frame: self.expand_large_data(p, v, nf),
                            anchor="w",
                            fg_color="transparent",
                            text_color=("gray30", "gray70"),
                            hover_color=("gray80", "gray20")
                        )
                        expand_button.pack(fill="x", padx=25, pady=2)
                        
                else:
                    # 创建叶子节点
                    leaf_frame = ctk.CTkFrame(parent)
                    leaf_frame.pack(fill="x", padx=5, pady=1)
                    
                    leaf_button = ctk.CTkButton(
                        leaf_frame,
                        text=f"📄 {key}: {str(value)[:30]}{'...' if len(str(value)) > 30 else ''}",
                        command=lambda p=current_path, v=value: self.select_leaf_node(p, v),
                        anchor="w",
                        fg_color="transparent",
                        text_color=("gray10", "gray90"),
                        hover_color=("gray80", "gray20")
                    )
                    leaf_button.pack(fill="x", padx=5, pady=1)
            
            # 如果还有更多项目，继续异步处理
            new_processed = processed_count + max_per_batch
            if new_processed < len(items):
                self.root.after(50, lambda: self._create_tree_nodes_async(parent, data, path_prefix, new_processed, max_per_batch))
            else:
                self.update_status('数据树加载完成')
        
        elif isinstance(data, list):
            # 处理列表类型
            for i, item in enumerate(data[:max_per_batch]):  # 限制显示数量
                current_path = f"{path_prefix}[{i}]" if path_prefix else f"[{i}]"
                
                item_frame = ctk.CTkFrame(parent)
                item_frame.pack(fill="x", padx=5, pady=1)
                
                item_button = ctk.CTkButton(
                    item_frame,
                    text=f"📋 [{i}]: {str(item)[:30]}{'...' if len(str(item)) > 30 else ''}",
                    command=lambda p=current_path, v=item: self.select_leaf_node(p, v),
                    anchor="w",
                    fg_color="transparent",
                    text_color=("gray10", "gray90"),
                    hover_color=("gray80", "gray20")
                )
                item_button.pack(fill="x", padx=5, pady=1)
            
            if len(data) > max_per_batch:
                remaining_count = len(data) - max_per_batch
                load_more_button = ctk.CTkButton(
                    parent,
                    text=f"📋 还有 {remaining_count} 个项目，点击加载更多...",
                    command=lambda: self.load_more_list_items(parent, data, path_prefix, max_per_batch),
                    anchor="w",
                    fg_color=("#3B82F6", "#1E40AF"),
                    text_color="white",
                    hover_color=("#2563EB", "#1D4ED8")
                )
                load_more_button.pack(fill="x", padx=25, pady=2)
            
            self.update_status('数据树加载完成')
    
    def _create_tree_nodes_simple(self, parent, data, path_prefix, start_index=0, items_per_page=10):
        """
        简单版本的树节点创建，支持分页加载
        """
        if isinstance(data, dict):
            items = list(data.items())
            end_index = start_index + items_per_page
            current_items = items[start_index:end_index]
            
            for key, value in current_items:
                current_path = f"{path_prefix}.{key}" if path_prefix else key
                
                if isinstance(value, (dict, list)):
                    # 创建可展开的节点
                    node_frame = ctk.CTkFrame(parent)
                    node_frame.pack(fill="x", padx=5, pady=1)
                    
                    node_button = ctk.CTkButton(
                        node_frame,
                        text=f"📁 {key}: {type(value).__name__} ({len(value)} items)",
                        command=lambda k=key, v=value, f=node_frame: self.expand_nested_data(f"{path_prefix}.{k}" if path_prefix else k, v, f),
                        anchor="w",
                        fg_color="transparent",
                        text_color=("gray10", "gray90"),
                        hover_color=("gray80", "gray20")
                    )
                    node_button.pack(fill="x", padx=5, pady=1)
                    
                else:
                    # 创建叶子节点
                    leaf_frame = ctk.CTkFrame(parent)
                    leaf_frame.pack(fill="x", padx=5, pady=1)
                    
                    leaf_button = ctk.CTkButton(
                        leaf_frame,
                        text=f"📄 {key}: {str(value)[:20]}{'...' if len(str(value)) > 20 else ''}",
                        command=lambda p=current_path, v=value: self.select_leaf_node(p, v),
                        anchor="w",
                        fg_color="transparent",
                        text_color=("gray10", "gray90"),
                        hover_color=("gray80", "gray20")
                    )
                    leaf_button.pack(fill="x", padx=5, pady=1)
            
            # 如果还有更多项目，显示可点击的加载更多按钮
            remaining_count = len(items) - end_index
            if remaining_count > 0:
                load_more_button = ctk.CTkButton(
                    parent,
                    text=f"📋 还有 {remaining_count} 个项目，点击加载更多...",
                    command=lambda: self.load_more_items(parent, data, path_prefix, end_index, items_per_page),
                    anchor="w",
                    fg_color=("#3B82F6", "#1E40AF"),
                    text_color="white",
                    hover_color=("#2563EB", "#1D4ED8")
                )
                load_more_button.pack(fill="x", padx=25, pady=2)
    
    def load_more_list_items(self, parent, data, path_prefix, start_index):
        """
        加载更多列表项目
        """
        # 移除"加载更多"按钮
        for widget in parent.winfo_children():
            if isinstance(widget, ctk.CTkButton) and "还有" in widget.cget("text") and "点击加载更多" in widget.cget("text"):
                widget.destroy()
                break
        
        # 继续显示更多列表项
        max_per_batch = 20
        end_index = start_index + max_per_batch
        
        for i, item in enumerate(data[start_index:end_index], start_index):
            current_path = f"{path_prefix}[{i}]" if path_prefix else f"[{i}]"
            
            item_frame = ctk.CTkFrame(parent)
            item_frame.pack(fill="x", padx=5, pady=1)
            
            item_button = ctk.CTkButton(
                item_frame,
                text=f"📋 [{i}]: {str(item)[:30]}{'...' if len(str(item)) > 30 else ''}",
                command=lambda p=current_path, v=item: self.select_leaf_node(p, v),
                anchor="w",
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray80", "gray20")
            )
            item_button.pack(fill="x", padx=5, pady=1)
        
        # 如果还有更多项目，继续显示加载更多按钮
        if end_index < len(data):
            remaining_count = len(data) - end_index
            load_more_button = ctk.CTkButton(
                parent,
                text=f"📋 还有 {remaining_count} 个项目，点击加载更多...",
                command=lambda: self.load_more_list_items(parent, data, path_prefix, end_index),
                anchor="w",
                fg_color=("#3B82F6", "#1E40AF"),
                text_color="white",
                hover_color=("#2563EB", "#1D4ED8")
            )
            load_more_button.pack(fill="x", padx=25, pady=2)
    
    def load_more_items(self, parent, data, path_prefix, start_index, items_per_page):
        """
        加载更多项目
        """
        # 移除"加载更多"按钮
        for widget in parent.winfo_children():
            if isinstance(widget, ctk.CTkButton) and "还有" in widget.cget("text") and "点击加载更多" in widget.cget("text"):
                widget.destroy()
                break
        
        # 继续加载更多项目
        self._create_tree_nodes_simple(parent, data, path_prefix, start_index, items_per_page)
    
    def expand_nested_data(self, path, data, node_frame):
        """
        展开嵌套文档数据
        """
        # 检查是否已经展开
        expanded = False
        for widget in node_frame.winfo_children():
            if isinstance(widget, ctk.CTkFrame) and widget.cget("fg_color") == "transparent":
                expanded = True
                break
        
        if expanded:
            # 如果已展开，则折叠
            for widget in list(node_frame.winfo_children()):
                if isinstance(widget, ctk.CTkFrame) and widget.cget("fg_color") == "transparent":
                    widget.destroy()
            # 更新按钮文本
            for widget in node_frame.winfo_children():
                if isinstance(widget, ctk.CTkButton):
                    current_text = widget.cget("text")
                    if current_text.startswith("📂"):
                        new_text = current_text.replace("📂", "📁")
                        widget.configure(text=new_text)
                    break
        else:
            # 如果未展开，则展开
            child_frame = ctk.CTkFrame(node_frame, fg_color="transparent")
            child_frame.pack(fill="x", padx=20, pady=2)
            
            # 显示加载提示
            loading_label = ctk.CTkLabel(child_frame, text="正在加载...")
            loading_label.pack(fill="x", padx=5, pady=2)
            
            # 更新按钮文本
            for widget in node_frame.winfo_children():
                if isinstance(widget, ctk.CTkButton):
                    current_text = widget.cget("text")
                    if current_text.startswith("📁"):
                        new_text = current_text.replace("📁", "📂")
                        widget.configure(text=new_text)
                    break
            
            # 异步加载内容
            self.root.after(100, lambda: self._load_nested_content(child_frame, data, path, loading_label))
    
    def _load_nested_content(self, parent, data, path, loading_label):
        """
        异步加载嵌套内容
        """
        # 移除加载提示
        loading_label.destroy()
        
        # 创建内容
        self._create_tree_nodes_simple(parent, data, path)
    
    def expand_large_data(self, path, data, node_frame):
        """
        展开/收回大数据内容
        """
        # 检查是否已经展开
        expanded = False
        for widget in node_frame.winfo_children():
            if isinstance(widget, ctk.CTkFrame) and widget.cget("fg_color") == "transparent":
                expanded = True
                break
        
        if expanded:
            # 如果已展开，则折叠
            for widget in list(node_frame.winfo_children()):
                if isinstance(widget, ctk.CTkFrame) and widget.cget("fg_color") == "transparent":
                    widget.destroy()
            # 重新创建展开按钮
            expand_button = ctk.CTkButton(
                node_frame,
                text="📋 点击展开查看内容...",
                command=lambda: self.expand_large_data(path, data, node_frame),
                anchor="w",
                fg_color=("#10B981", "#059669"),
                text_color="white",
                hover_color=("#059669", "#047857")
            )
            expand_button.pack(fill="x", padx=25, pady=2)
        else:
            # 如果未展开，则展开
            # 移除展开按钮
            for widget in node_frame.winfo_children():
                if isinstance(widget, ctk.CTkButton) and "点击展开" in widget.cget("text"):
                    widget.destroy()
                    break
            
            # 创建子框架显示内容
            child_frame = ctk.CTkFrame(node_frame, fg_color="transparent")
            child_frame.pack(fill="x", padx=20)
            
            # 显示加载提示
            loading_label = ctk.CTkLabel(child_frame, text="正在加载...")
            loading_label.pack(fill="x", padx=5, pady=2)
            
            # 异步加载内容
            self.root.after(100, lambda: self._load_large_data_content(child_frame, data, path, loading_label))
    
    def _load_large_data_content(self, parent, data, path, loading_label):
        """
        异步加载大数据内容
        """
        # 移除加载提示
        loading_label.destroy()
        
        # 创建内容
        self._create_tree_nodes_simple(parent, data, path)
    
    def _create_tree_nodes(self, parent, data, path_prefix):
        """
        递归创建树节点
        """
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path_prefix}.{key}" if path_prefix else key
                
                if isinstance(value, (dict, list)):
                    # 创建可展开的节点
                    node_frame = ctk.CTkFrame(parent)
                    node_frame.pack(fill="x", padx=5, pady=2)
                    
                    node_button = ctk.CTkButton(
                        node_frame,
                        text=f"📁 {key}",
                        command=lambda p=current_path: self.select_node(p),
                        anchor="w",
                        fg_color="transparent",
                        text_color=("gray10", "gray90"),
                        hover_color=("gray80", "gray20")
                    )
                    node_button.pack(fill="x", padx=5, pady=2)
                    
                    # 递归创建子节点
                    child_frame = ctk.CTkFrame(node_frame, fg_color="transparent")
                    child_frame.pack(fill="x", padx=20)
                    self._create_tree_nodes(child_frame, value, current_path)
                    
                else:
                    # 创建叶子节点
                    leaf_frame = ctk.CTkFrame(parent)
                    leaf_frame.pack(fill="x", padx=5, pady=1)
                    
                    leaf_button = ctk.CTkButton(
                        leaf_frame,
                        text=f"📄 {key}: {str(value)[:30]}{'...' if len(str(value)) > 30 else ''}",
                        command=lambda p=current_path, v=value: self.select_leaf_node(p, v),
                        anchor="w",
                        fg_color="transparent",
                        text_color=("gray10", "gray90"),
                        hover_color=("gray80", "gray20")
                    )
                    leaf_button.pack(fill="x", padx=5, pady=1)
        
        elif isinstance(data, list):
            for i, item in enumerate(data):
                current_path = f"{path_prefix}[{i}]" if path_prefix else f"[{i}]"
                
                if isinstance(item, (dict, list)):
                    # 创建数组节点
                    node_frame = ctk.CTkFrame(parent)
                    node_frame.pack(fill="x", padx=5, pady=2)
                    
                    node_button = ctk.CTkButton(
                        node_frame,
                        text=f"📋 [{i}]",
                        command=lambda p=current_path: self.select_node(p),
                        anchor="w",
                        fg_color="transparent",
                        text_color=("gray10", "gray90"),
                        hover_color=("gray80", "gray20")
                    )
                    node_button.pack(fill="x", padx=5, pady=2)
                    
                    # 递归创建子节点
                    child_frame = ctk.CTkFrame(node_frame, fg_color="transparent")
                    child_frame.pack(fill="x", padx=20)
                    self._create_tree_nodes(child_frame, item, current_path)
                    
                else:
                    # 创建数组元素节点
                    leaf_frame = ctk.CTkFrame(parent)
                    leaf_frame.pack(fill="x", padx=5, pady=1)
                    
                    leaf_button = ctk.CTkButton(
                        leaf_frame,
                        text=f"📄 [{i}]: {str(item)[:30]}{'...' if len(str(item)) > 30 else ''}",
                        command=lambda p=current_path, v=item: self.select_leaf_node(p, v),
                        anchor="w",
                        fg_color="transparent",
                        text_color=("gray10", "gray90"),
                        hover_color=("gray80", "gray20")
                    )
                    leaf_button.pack(fill="x", padx=5, pady=1)
    
    def select_node(self, path):
        """
        选择节点（容器节点）
        """
        self.current_path = path
        self.path_label.configure(text=f"路径: {path}")
        self.value_entry.delete(0, "end")
        self.value_entry.configure(placeholder_text="此节点包含子项，无法直接编辑")
        self.update_button.configure(state="disabled")
        self.type_label.configure(text="类型: 容器节点")
    
    def select_leaf_node(self, path, value):
        """
        选择叶子节点（可编辑节点）
        """
        self.current_path = path
        self.current_value = value
        self.path_label.configure(text=f"路径: {path}")
        
        # 设置当前值
        self.value_entry.delete(0, "end")
        self.value_entry.insert(0, str(value))
        self.value_entry.configure(placeholder_text="")
        
        # 启用更新按钮
        self.update_button.configure(state="normal")
        
        # 显示数据类型
        value_type = type(value).__name__
        self.type_label.configure(text=f"类型: {value_type}")
    
    def update_value(self):
        """
        更新选中节点的值
        """
        if not hasattr(self, 'current_path') or not hasattr(self, 'current_value'):
            return
        
        try:
            new_value = self.value_entry.get()
            
            # 尝试转换为原始数据类型
            if isinstance(self.current_value, bool):
                new_value = new_value.lower() in ('true', '1', 'yes', 'on')
            elif isinstance(self.current_value, int):
                new_value = int(new_value)
            elif isinstance(self.current_value, float):
                new_value = float(new_value)
            # 字符串保持原样
            
            # 更新数据
            self.set_value_from_path(self.data, self.current_path, new_value)
            self.modified = True
            
            # 只更新当前显示的值，不刷新整个树视图以保持展开状态
            self.current_value = new_value
            
            # 更新左侧树视图中对应节点的显示值
            self._update_tree_node_display(self.current_path, new_value)
            
            self.update_status(f'已更新: {self.current_path} = {new_value}')
            
        except ValueError as e:
            messagebox.showerror('错误', f'值转换失败: {str(e)}')
        except Exception as e:
            messagebox.showerror('错误', f'更新值失败: {str(e)}')
    
    def _update_tree_node_display(self, path, new_value):
        """
        更新树视图中对应节点的显示值
        """
        try:
            # 递归查找并更新对应路径的叶子节点按钮
            self._find_and_update_node_button(self.tree_scroll_frame, path, new_value)
        except Exception as e:
            print(f"更新树节点显示失败: {e}")
    
    def _find_and_update_node_button(self, parent, target_path, new_value):
        """
        递归查找并更新指定路径的节点按钮文本
        """
        for widget in parent.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                # 检查这个框架中的按钮
                for child in widget.winfo_children():
                    if isinstance(child, ctk.CTkButton):
                        button_text = child.cget("text")
                        # 检查是否是叶子节点按钮
                        if button_text.startswith("📄"):
                            # 从按钮的command中获取路径信息
                            try:
                                # 通过按钮文本推断路径
                                if self._is_target_leaf_button(button_text, target_path):
                                    # 更新按钮文本
                                    key = target_path.split('.')[-1] if '.' in target_path else target_path
                                    key = key.replace('[', '').replace(']', '') if '[' in key else key
                                    new_text = f"📄 {key}: {str(new_value)[:20]}{'...' if len(str(new_value)) > 20 else ''}"
                                    child.configure(text=new_text)
                                    return True
                            except:
                                pass
                # 递归搜索子框架
                if self._find_and_update_node_button(widget, target_path, new_value):
                    return True
        return False
    
    def _is_target_leaf_button(self, button_text, target_path):
        """
        判断按钮是否对应目标路径
        """
        try:
            # 从路径中提取最后一个键名
            if '.' in target_path:
                key = target_path.split('.')[-1]
            else:
                key = target_path
            
            # 处理数组索引
            if '[' in key and ']' in key:
                key = key.replace('[', '').replace(']', '')
            
            # 检查按钮文本是否包含这个键名
            return f"📄 {key}:" in button_text
        except:
            return False
    
    def set_value_from_path(self, data, path, value):
        """
        根据路径设置值
        """
        parts = []
        current_part = ""
        in_brackets = False
        
        for char in path:
            if char == '[':
                if current_part:
                    parts.append(current_part)
                    current_part = ""
                in_brackets = True
            elif char == ']':
                if current_part:
                    parts.append(int(current_part))
                    current_part = ""
                in_brackets = False
            elif char == '.' and not in_brackets:
                if current_part:
                    parts.append(current_part)
                    current_part = ""
            else:
                current_part += char
        
        if current_part:
            if in_brackets:
                parts.append(int(current_part))
            else:
                parts.append(current_part)
        
        # 导航到目标位置并设置值
        current = data
        for part in parts[:-1]:
            current = current[part]
        
        current[parts[-1]] = value
    
    def show_about(self):
        """
        显示关于对话框
        """
        about_window = ctk.CTkToplevel(self.root)
        about_window.title("关于")
        about_window.geometry("400x300")
        about_window.resizable(False, False)
        
        # 居中显示
        about_window.transient(self.root)
        about_window.grab_set()
        
        # 内容
        content_frame = ctk.CTkFrame(about_window)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            content_frame,
            text="🎮 Silk 存档编辑器",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(20, 10))
        
        version_label = ctk.CTkLabel(
            content_frame,
            text="现代版 v2.0",
            font=ctk.CTkFont(size=14)
        )
        version_label.pack(pady=5)
        
        description_label = ctk.CTkLabel(
            content_frame,
            text="一个现代化的游戏存档编辑工具\n\n支持多种文件格式:\n• DAT 文件\n• JSON 文件\n• XML 文件\n\n使用 CustomTkinter 构建",
            font=ctk.CTkFont(size=12),
            justify="center"
        )
        description_label.pack(pady=20)
        
        close_button = ctk.CTkButton(
            content_frame,
            text="关闭",
            command=about_window.destroy,
            width=100
        )
        close_button.pack(pady=(0, 20))