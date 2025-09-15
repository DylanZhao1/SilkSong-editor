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
        
        # 搜索相关变量
        self.search_results = []
        self.current_search_term = ""
        self.original_tree_data = None
        
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
            text="🎮 SilkSong 存档编辑器", 
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
        
        # 搜索框
        search_frame = ctk.CTkFrame(button_frame, fg_color="transparent")
        search_frame.pack(side="right", padx=10)
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="🔍 搜索关键词...",
            width=200,
            height=35
        )
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<Return>", self.search_keys)
        
        self.search_button = ctk.CTkButton(
            search_frame,
            text="搜索",
            command=self.search_keys,
            width=60,
            height=35
        )
        self.search_button.pack(side="left", padx=2)
        
        self.clear_search_button = ctk.CTkButton(
            search_frame,
            text="清除",
            command=self.clear_search,
            width=60,
            height=35,
            fg_color="gray",
            hover_color="darkgray"
        )
        self.clear_search_button.pack(side="left", padx=2)
        
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
        
        # 绑定滚动事件来自动加载更多内容
        self._bind_scroll_events()
        
        # 存储当前数据和加载状态
        self.current_data = None
        self.current_path_prefix = ""
        self.is_loading_more = False
        
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
    
    def _bind_scroll_events(self):
        """
        绑定滚动事件来自动加载更多内容
        """
        # 获取内部的canvas和scrollbar
        canvas = None
        for child in self.tree_scroll_frame.winfo_children():
            if hasattr(child, 'winfo_class') and child.winfo_class() == 'Canvas':
                canvas = child
                break
        
        if canvas:
            # 绑定鼠标滚轮事件
            canvas.bind('<MouseWheel>', self._on_mousewheel)
            # 绑定滚动条事件
            canvas.bind('<Configure>', self._on_canvas_configure)
    
    def _on_mousewheel(self, event):
        """
        处理鼠标滚轮事件
        """
        # 检查是否滚动到底部
        self.root.after(50, self._check_scroll_position)
    
    def _on_canvas_configure(self, event):
        """
        处理canvas配置变化事件
        """
        # 检查是否滚动到底部
        self.root.after(50, self._check_scroll_position)
    
    def _check_scroll_position(self):
        """
        检查滚动位置，如果接近底部则自动加载更多内容
        """
        if self.is_loading_more:
            return
            
        # 获取滚动框架的canvas
        canvas = None
        for child in self.tree_scroll_frame.winfo_children():
            if hasattr(child, 'winfo_class') and child.winfo_class() == 'Canvas':
                canvas = child
                break
        
        if canvas:
            # 获取滚动位置
            try:
                scroll_top = canvas.canvasy(0)
                scroll_bottom = canvas.canvasy(canvas.winfo_height())
                canvas_height = canvas.bbox("all")[3] if canvas.bbox("all") else 0
                
                # 如果滚动到接近底部（90%），自动加载更多
                if canvas_height > 0 and scroll_bottom >= canvas_height * 0.9:
                    self._auto_load_more()
            except:
                pass
    
    def _auto_load_more(self):
        """
        自动加载更多内容
        """
        if self.is_loading_more:
            return
            
        # 查找"加载更多"按钮并自动点击
        self._find_and_click_load_more_button(self.tree_scroll_frame)
    
    def _find_and_click_load_more_button(self, parent):
        """
        递归查找并点击"加载更多"按钮
        """
        for widget in parent.winfo_children():
            if isinstance(widget, ctk.CTkButton):
                button_text = widget.cget("text")
                if "还有" in button_text and "点击加载更多" in button_text:
                    self.is_loading_more = True
                    # 模拟点击按钮
                    widget.invoke()
                    # 延迟重置加载状态
                    self.root.after(1000, lambda: setattr(self, 'is_loading_more', False))
                    return True
            elif hasattr(widget, 'winfo_children'):
                if self._find_and_click_load_more_button(widget):
                    return True
        return False
    
    def _create_status_bar(self):
        """
        创建状态栏
        """
        status_frame = ctk.CTkFrame(self.root, height=30, corner_radius=0)
        status_frame.pack(side="bottom", fill="x")
        status_frame.pack_propagate(False)
        
        # 状态标签
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="就绪",
            font=ctk.CTkFont(size=12),
            anchor="w"
        )
        self.status_label.pack(side="left", padx=20, pady=5)
        
        # 文件信息标签
        self.file_info_label = ctk.CTkLabel(
            status_frame,
            text="",
            font=ctk.CTkFont(size=12),
            anchor="e"
        )
        self.file_info_label.pack(side="right", padx=20, pady=5)
    
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
            # 存储当前数据和状态
            self.current_data = self.data
            self.current_path_prefix = ""
            self.is_loading_more = False
            
            # 显示加载提示
            self.update_status('正在加载数据树...')
            # 使用after方法异步创建树节点，避免界面卡死
            self.root.after(100, lambda: self._create_tree_nodes_async(self.tree_scroll_frame, self.data, ""))
            # 延迟绑定滚动事件，确保内容已加载
            self.root.after(1000, self._bind_scroll_events)
    
    def _create_tree_nodes_async(self, parent, data, path_prefix, processed_count=0, max_per_batch=100):
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
    
    def _calculate_json_lines(self, data):
        """
        计算JSON数据的行数（用于分页控制）
        """
        if isinstance(data, dict):
            if not data:
                return 2  # {} 空字典占2行
            lines = 1  # 开始的 {
            for key, value in data.items():
                lines += 1  # key行
                if isinstance(value, (dict, list)):
                    lines += self._calculate_json_lines(value)
                else:
                    # 简单值不额外增加行数，已在key行计算
                    pass
            lines += 1  # 结束的 }
            return lines
        elif isinstance(data, list):
            if not data:
                return 2  # [] 空列表占2行
            lines = 1  # 开始的 [
            for item in data:
                if isinstance(item, (dict, list)):
                    lines += self._calculate_json_lines(item)
                else:
                    lines += 1  # 简单值占1行
            lines += 1  # 结束的 ]
            return lines
        else:
            return 1  # 简单值占1行
    
    def _create_tree_nodes_simple(self, parent, data, path_prefix, start_index=0, items_per_page=100):
        """
        简单版本的树节点创建，支持基于行数的分页加载
        """
        if isinstance(data, dict):
            items = list(data.items())
            current_lines = 0
            processed_items = 0
            
            for i, (key, value) in enumerate(items[start_index:], start_index):
                # 计算当前项的行数
                if isinstance(value, (dict, list)):
                    item_lines = 1 + self._calculate_json_lines(value)  # key行 + 值的行数
                else:
                    item_lines = 1  # 简单值只占1行
                
                # 检查是否超过页面限制
                if current_lines + item_lines > items_per_page and processed_items > 0:
                    # 创建"加载更多"按钮
                    load_more_frame = ctk.CTkFrame(parent)
                    load_more_frame.pack(fill="x", padx=5, pady=5)
                    
                    load_more_button = ctk.CTkButton(
                        load_more_frame,
                        text=f"📥 加载更多... (剩余 {len(items) - i} 项)",
                        command=lambda p=parent, d=data, pp=path_prefix, si=i: self._create_tree_nodes_simple(p, d, pp, si, items_per_page),
                        fg_color=("#1f538d", "#14375e"),
                        hover_color=("#144870", "#1f538d")
                    )
                    load_more_button.pack(fill="x", padx=5, pady=2)
                    break
                
                current_path = f"{path_prefix}.{key}" if path_prefix else key
                
                if isinstance(value, (dict, list)):
                    # 创建展开的节点标题
                    node_frame = ctk.CTkFrame(parent)
                    node_frame.pack(fill="x", padx=5, pady=1)
                    
                    node_button = ctk.CTkButton(
                        node_frame,
                        text=f"📂 {key}: {type(value).__name__} ({len(value)} items)",
                        command=lambda p=current_path, v=value: self.select_leaf_node(p, v),
                        anchor="w",
                        fg_color="transparent",
                        text_color=("gray10", "gray90"),
                        hover_color=("gray80", "gray20")
                    )
                    node_button.pack(fill="x", padx=5, pady=1)
                    
                    # 自动展开嵌套内容
                    child_frame = ctk.CTkFrame(node_frame, fg_color="transparent")
                    child_frame.pack(fill="x", padx=20, pady=2)
                    self._create_tree_nodes_simple(child_frame, value, current_path)
                    
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
                
                # 更新行数和处理项目计数
                current_lines += item_lines
                processed_items += 1
        
        elif isinstance(data, list):
            # 处理列表类型数据，基于行数分页
            current_lines = 0
            processed_items = 0
            
            for i in range(start_index, len(data)):
                item = data[i]
                
                # 计算当前项的行数
                if isinstance(item, (dict, list)):
                    item_lines = self._calculate_json_lines(item)
                else:
                    item_lines = 1  # 简单值占1行
                
                # 检查是否超过页面限制
                if current_lines + item_lines > items_per_page and processed_items > 0:
                    # 创建"加载更多"按钮
                    load_more_frame = ctk.CTkFrame(parent)
                    load_more_frame.pack(fill="x", padx=5, pady=5)
                    
                    load_more_button = ctk.CTkButton(
                        load_more_frame,
                        text=f"📥 加载更多... (剩余 {len(data) - i} 项)",
                        command=lambda p=parent, d=data, pp=path_prefix, si=i: self._create_tree_nodes_simple(p, d, pp, si, items_per_page),
                        fg_color=("#1f538d", "#14375e"),
                        hover_color=("#144870", "#1f538d")
                    )
                    load_more_button.pack(fill="x", padx=5, pady=2)
                    break
                current_path = f"{path_prefix}[{i}]" if path_prefix else f"[{i}]"
                
                if isinstance(item, (dict, list)):
                    # 创建展开的节点标题
                    node_frame = ctk.CTkFrame(parent)
                    node_frame.pack(fill="x", padx=5, pady=1)
                    
                    # 尝试获取有意义的名称
                    display_name = f"[{i}]"
                    if isinstance(item, dict) and 'Name' in item:
                        display_name = str(item['Name'])
                    elif isinstance(item, dict) and 'name' in item:
                        display_name = str(item['name'])
                    
                    node_button = ctk.CTkButton(
                        node_frame,
                        text=f"📂 {display_name}: {type(item).__name__} ({len(item)} items)",
                        command=lambda p=current_path, v=item: self.select_leaf_node(p, v),
                        anchor="w",
                        fg_color="transparent",
                        text_color=("gray10", "gray90"),
                        hover_color=("gray80", "gray20")
                    )
                    node_button.pack(fill="x", padx=5, pady=1)
                    
                    # 自动展开嵌套内容
                    child_frame = ctk.CTkFrame(node_frame, fg_color="transparent")
                    child_frame.pack(fill="x", padx=20, pady=2)
                    self._create_tree_nodes_simple(child_frame, item, current_path)
                    
                else:
                    # 创建叶子节点
                    leaf_frame = ctk.CTkFrame(parent)
                    leaf_frame.pack(fill="x", padx=5, pady=1)
                    
                    leaf_button = ctk.CTkButton(
                        leaf_frame,
                        text=f"📄 [{i}]: {str(item)[:20]}{'...' if len(str(item)) > 20 else ''}",
                        command=lambda p=current_path, v=item: self.select_leaf_node(p, v),
                        anchor="w",
                        fg_color="transparent",
                        text_color=("gray10", "gray90"),
                        hover_color=("gray80", "gray20")
                    )
                    leaf_button.pack(fill="x", padx=5, pady=1)
                
                # 更新行数和处理项目计数
                current_lines += item_lines
                processed_items += 1
    
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
        max_per_batch = 50
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
    
    def search_keys(self, event=None):
        """
        搜索包含关键词的key
        """
        if not self.data:
            messagebox.showwarning("警告", "请先加载文件")
            return
            
        search_term = self.search_entry.get().strip()
        if not search_term:
            messagebox.showwarning("警告", "请输入搜索关键词")
            return
            
        self.current_search_term = search_term.lower()
        self.search_results = []
        
        # 保存原始数据用于恢复
        if self.original_tree_data is None:
            self.original_tree_data = self.data
            
        # 搜索匹配的键值对
        self._search_in_data(self.data, "")
        
        if self.search_results:
            # 显示搜索结果
            self._display_search_results()
            self.update_status(f"找到 {len(self.search_results)} 个匹配项")
        else:
            messagebox.showinfo("搜索结果", f"未找到包含 '{search_term}' 的键")
            self.update_status("未找到匹配项")
    
    def _search_in_data(self, data, path_prefix):
        """
        递归搜索数据中包含关键词的key
        """
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path_prefix}.{key}" if path_prefix else key
                
                # 检查key是否包含搜索词
                if self.current_search_term in key.lower():
                    self.search_results.append({
                        'path': current_path,
                        'key': key,
                        'value': value,
                        'type': type(value).__name__
                    })
                
                # 递归搜索嵌套数据
                if isinstance(value, (dict, list)):
                    self._search_in_data(value, current_path)
                    
        elif isinstance(data, list):
            for i, item in enumerate(data):
                current_path = f"{path_prefix}[{i}]" if path_prefix else f"[{i}]"
                
                # 对于列表项，如果是字典则搜索其键
                if isinstance(item, dict):
                    self._search_in_data(item, current_path)
                elif isinstance(item, list):
                    self._search_in_data(item, current_path)
    
    def _display_search_results(self):
        """
        显示搜索结果
        """
        # 清空当前树视图
        for widget in self.tree_scroll_frame.winfo_children():
            widget.destroy()
            
        # 创建搜索结果标题
        result_title = ctk.CTkLabel(
            self.tree_scroll_frame,
            text=f"🔍 搜索结果: '{self.current_search_term}' ({len(self.search_results)} 项)",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        result_title.pack(fill="x", padx=10, pady=10)
        
        # 添加返回主页按钮
        back_button_frame = ctk.CTkFrame(self.tree_scroll_frame, fg_color="transparent")
        back_button_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        back_button = ctk.CTkButton(
            back_button_frame,
            text="🏠 返回主页",
            command=self._return_to_main_view,
            width=120,
            height=30,
            font=ctk.CTkFont(size=12),
            fg_color=("#DC2626", "#EF4444"),
            hover_color=("#B91C1C", "#DC2626")
        )
        back_button.pack(anchor="w")
        
        # 显示每个搜索结果
        for result in self.search_results:
            self._create_search_result_item(result)
    
    def _create_search_result_item(self, result):
        """
        创建搜索结果项
        """
        result_frame = ctk.CTkFrame(self.tree_scroll_frame)
        result_frame.pack(fill="x", padx=10, pady=2)
        
        # 路径显示
        path_label = ctk.CTkLabel(
            result_frame,
            text=f"📍 {result['path']}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#2563EB", "#60A5FA")
        )
        path_label.pack(anchor="w", padx=10, pady=(5, 0))
        
        # 键值显示
        if isinstance(result['value'], (dict, list)):
            value_text = f"{result['type']} ({len(result['value'])} items)"
        else:
            value_text = str(result['value'])[:50] + ("..." if len(str(result['value'])) > 50 else "")
            
        key_value_frame = ctk.CTkFrame(result_frame, fg_color="transparent")
        key_value_frame.pack(fill="x", padx=10, pady=5)
        
        # 高亮显示匹配的key
        key_text = result['key']
        highlighted_key = key_text.replace(
            self.current_search_term, 
            f"🔥{self.current_search_term.upper()}🔥"
        )
        
        key_label = ctk.CTkLabel(
            key_value_frame,
            text=f"🔑 {highlighted_key}: {value_text}",
            font=ctk.CTkFont(size=11)
        )
        key_label.pack(anchor="w")
        
        # 按钮框架
        button_frame = ctk.CTkFrame(result_frame, fg_color="transparent")
        button_frame.pack(anchor="e", padx=10, pady=(0, 5))
        
        # 添加到右侧按钮
        add_button = ctk.CTkButton(
            button_frame,
            text="➕ 添加到右侧",
            command=lambda r=result: self._add_to_right_panel(r),
            width=100,
            height=25,
            font=ctk.CTkFont(size=10),
            fg_color=("#16A34A", "#22C55E"),
            hover_color=("#15803D", "#16A34A")
        )
        add_button.pack(side="left", padx=(0, 5))
        
        # 查看按钮 - 所有结果都可以点击查看上下文
        view_button = ctk.CTkButton(
            button_frame,
            text="👁️ 查看上下文",
            command=lambda r=result: self._edit_search_result(r),
            width=100,
            height=25,
            font=ctk.CTkFont(size=10)
        )
        view_button.pack(side="left")
    
    def _return_to_main_view(self):
        """
        返回主页视图，清除搜索结果并重新显示树形结构
        """
        # 清除搜索相关状态
        self.search_results = []
        self.current_search_term = ""
        
        # 清空搜索框
        if hasattr(self, 'search_entry'):
            self.search_entry.delete(0, 'end')
        
        # 重新填充树形视图
        self.populate_tree_modern()
        
        # 更新状态栏
        self.update_status("已返回主页视图")
    
    def _add_to_right_panel(self, result):
        """
        将搜索结果添加到右侧编辑面板
        """
        # 直接选择该节点，这会在右侧显示编辑界面
        self.select_leaf_node(result['path'], result['value'])
        
        # 更新状态栏
        self.update_status(f"已添加到右侧编辑面板: {result['path']}")
        
        # 可选：清除搜索结果，专注于编辑
        # self.clear_search()
    
    def _edit_search_result(self, result):
        """
        编辑搜索结果项，展示上下文内容
        """
        # 清除搜索结果，显示上下文
        self._show_search_context(result)
        
    def _show_search_context(self, result):
        """
        显示搜索结果的上下文内容（上下25行）
        """
        # 清空当前树视图
        for widget in self.tree_scroll_frame.winfo_children():
            widget.destroy()
            
        # 创建上下文标题
        context_title = ctk.CTkLabel(
            self.tree_scroll_frame,
            text=f"🎯 上下文视图: {result['path']}",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        context_title.pack(fill="x", padx=10, pady=10)
        
        # 返回按钮
        back_button = ctk.CTkButton(
            self.tree_scroll_frame,
            text="← 返回搜索结果",
            command=self._display_search_results,
            width=120,
            height=30
        )
        back_button.pack(anchor="w", padx=10, pady=(0, 10))
        
        # 获取上下文数据
        context_data = self._get_context_data(result, 25)
        
        # 显示上下文内容
        for i, (path, key, value, is_target) in enumerate(context_data):
            self._create_context_item(path, key, value, is_target, result['key'])
    
    def _get_context_data(self, target_result, context_lines):
        """
        获取目标结果周围的上下文数据
        """
        context_data = []
        target_path = target_result['path']
        
        # 递归收集所有数据项
        all_items = []
        if self.data:
            self._collect_all_items(self.data, "", all_items)
        else:
            return context_data
        
        # 找到目标项的索引
        target_index = -1
        for i, (path, key, value) in enumerate(all_items):
            if path == target_path:
                target_index = i
                break
                
        if target_index == -1:
            return context_data
            
        # 获取上下文范围
        start_index = max(0, target_index - context_lines)
        end_index = min(len(all_items), target_index + context_lines + 1)
        
        # 构建上下文数据
        for i in range(start_index, end_index):
            path, key, value = all_items[i]
            is_target = (i == target_index)
            context_data.append((path, key, value, is_target))
            
        return context_data
        
    def _collect_all_items(self, data, path_prefix, items_list):
        """
        递归收集所有数据项
        """
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path_prefix}.{key}" if path_prefix else key
                items_list.append((current_path, key, value))
                if isinstance(value, (dict, list)):
                    self._collect_all_items(value, current_path, items_list)
        elif isinstance(data, list):
            for i, value in enumerate(data):
                current_path = f"{path_prefix}[{i}]"
                items_list.append((current_path, f"[{i}]", value))
                if isinstance(value, (dict, list)):
                    self._collect_all_items(value, current_path, items_list)
                    
    def _create_context_item(self, path, key, value, is_target, search_term):
        """
        创建上下文项
        """
        # 根据是否为目标项选择不同的样式
        if is_target:
            item_frame = ctk.CTkFrame(self.tree_scroll_frame, fg_color=("#FEF3C7", "#92400E"))  # 黄色高亮
        else:
            item_frame = ctk.CTkFrame(self.tree_scroll_frame)
            
        item_frame.pack(fill="x", padx=10, pady=1)
        
        # 路径显示
        path_label = ctk.CTkLabel(
            item_frame,
            text=f"📍 {path}",
            font=ctk.CTkFont(size=10),
            text_color=("#6B7280", "#9CA3AF")
        )
        path_label.pack(anchor="w", padx=10, pady=(2, 0))
        
        # 键值显示
        if isinstance(value, (dict, list)):
            value_text = f"{type(value).__name__} ({len(value)} items)"
        else:
            value_text = str(value)[:100] + ("..." if len(str(value)) > 100 else "")
            
        # 高亮搜索词
        if is_target and search_term.lower() in key.lower():
            key_text = key.replace(search_term, f"🔥{search_term.upper()}🔥")
        else:
            key_text = key
            
        key_value_label = ctk.CTkLabel(
            item_frame,
            text=f"🔑 {key_text}: {value_text}",
            font=ctk.CTkFont(size=11, weight="bold" if is_target else "normal")
        )
        key_value_label.pack(anchor="w", padx=10, pady=(0, 2))
        
        # 如果是目标项且不是复合类型，添加编辑按钮
        if is_target and not isinstance(value, (dict, list)):
            edit_button = ctk.CTkButton(
                item_frame,
                text="✏️ 编辑此项",
                command=lambda: self.select_leaf_node(path, value),
                width=80,
                height=25,
                font=ctk.CTkFont(size=10)
            )
            edit_button.pack(anchor="e", padx=10, pady=(0, 5))

    def clear_search(self):
        """
        清除搜索结果，恢复原始视图
        """
        self.search_entry.delete(0, 'end')
        self.current_search_term = ""
        self.search_results = []
        
        if self.original_tree_data:
            # 恢复原始树视图
            self.populate_tree_modern()
            self.update_status("已清除搜索结果")
    
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