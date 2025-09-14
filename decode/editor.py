import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import shutil
from datetime import datetime
import base64
from Crypto.Cipher import AES

class SaveEditor:
        
    def remove_header(self, data):
        try:
            # C# fixed header
            csharp_header = bytes([0, 1, 0, 0, 0, 255, 255, 255, 255, 1, 0, 0, 0, 0, 0, 0, 0, 6, 1, 0, 0, 0])
            
            # Remove fixed header and ending byte 11
            data = data[len(csharp_header):-1]
            
            # Remove LengthPrefixedString header
            length_count = 0
            for i in range(5):
                length_count += 1
                if (data[i] & 0x80) == 0:
                    break
            
            data = data[length_count:]
            return data
        except Exception as e:
            messagebox.showerror('错误', f'移除头部时出错: {str(e)}')
            return None
    
    def decrypt_data(self, data):
        try:
            # Base64 decode
            decoded = base64.b64decode(data)
            
            # AES key
            key = 'UKu52ePUBwetZ9wNX88o54dnfKRu0T1l'.encode('utf-8')[:32]
            
            # Create AES cipher in ECB mode
            cipher = AES.new(key, AES.MODE_ECB)
            
            # Decrypt
            decrypted = cipher.decrypt(decoded)
            
            # Remove PKCS7 padding
            padding_length = decrypted[-1]
            decrypted = decrypted[:-padding_length]
            
            # Convert to string and parse JSON
            result = decrypted.decode('utf-8')
            
            return result
        except Exception as e:
            messagebox.showerror('错误', f'解密数据时出错: {str(e)}')
            return None
    
    def encrypt_data(self, json_str):
        try:
            # 将JSON字符串转换为字节
            data = json_str.encode('utf-8')
            
            # AES key
            key = 'UKu52ePUBwetZ9wNX88o54dnfKRu0T1l'.encode('utf-8')[:32]
            
            # Create AES cipher in ECB mode
            cipher = AES.new(key, AES.MODE_ECB)
            
            # PKCS7 padding
            pad_value = 16 - (len(data) % 16)
            padded = data + bytes([pad_value] * pad_value)
            
            # Encrypt
            encrypted = cipher.encrypt(padded)
            
            # Base64 encode - 使用标准Base64编码，不过滤换行符
            encoded = base64.b64encode(encrypted)
            
            # Add header
            return self.add_header(encoded)
        except Exception as e:
            messagebox.showerror('错误', f'加密数据时出错: {str(e)}')
            return None
    
    def generate_length_prefixed_string(self, length):
        length = min(0x7FFFFFFF, length)  # maximum value
        bytes_list = []
        for i in range(4):
            if length >> 7 != 0:
                bytes_list.append(length & 0x7F | 0x80)
                length >>= 7
            else:
                bytes_list.append(length & 0x7F)
                length >>= 7
                break
        if length != 0:
            bytes_list.append(length)
        return bytes(bytes_list)
    
    def add_header(self, data):
        # C# fixed header
        csharp_header = bytes([0, 1, 0, 0, 0, 255, 255, 255, 255, 1, 0, 0, 0, 0, 0, 0, 0, 6, 1, 0, 0, 0])
        
        # Generate LengthPrefixedString header
        length_data = self.generate_length_prefixed_string(len(data))
        
        # Combine all parts
        result = bytearray(csharp_header)
        result.extend(length_data)
        result.extend(data)
        result.append(11)  # fixed ending byte
        
        return bytes(result)
    
    def __init__(self, root):
        self.root = root
        self.root.title('存档编辑器')
        self.root.geometry('800x600')
        
        self.data = None
        self.file_path = None
        self.modified = False
        
        # 创建菜单栏
        self.menu_bar = tk.Menu(root)
        self.root.config(menu=self.menu_bar)
        
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label='文件', menu=self.file_menu)
        self.file_menu.add_command(label='打开...', command=self.load_file)
        self.file_menu.add_command(label='保存', command=self.save_file)
        self.file_menu.add_command(label='另存为游戏存档...', command=self.save_as_game_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label='退出', command=root.quit)
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建树形视图
        self.tree_frame = ttk.Frame(self.main_frame)
        self.tree_frame.pack(fill=tk.BOTH, expand=True, side=tk.TOP)
        
        self.tree = ttk.Treeview(self.tree_frame)
        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # 添加滚动条
        self.scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        
        # 设置树形视图列
        self.tree["columns"] = ("value")
        self.tree.column("#0", width=300, minwidth=200)
        self.tree.column("value", width=400, minwidth=200)
        
        self.tree.heading("#0", text="键")
        self.tree.heading("value", text="值")
        
        # 绑定选择事件
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        # 创建值编辑框架
        self.edit_frame = ttk.Frame(self.main_frame, padding="5")
        self.edit_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=10)
        
        ttk.Label(self.edit_frame, text="值:").pack(side=tk.LEFT, padx=5)
        
        self.value_entry = ttk.Entry(self.edit_frame, width=50)
        self.value_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.update_button = ttk.Button(self.edit_frame, text="更新", command=self.update_value)
        self.update_button.pack(side=tk.LEFT, padx=5)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set('准备就绪')
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 设置关闭窗口事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def on_close(self):
        if self.modified:
            response = messagebox.askyesnocancel('保存更改', '文件已修改，是否保存更改？')
            if response is None:  # 取消
                return
            elif response:  # 是
                self.save_file()
        self.root.destroy()
    
    def load_file(self):
        if self.modified:
            response = messagebox.askyesnocancel('保存更改', '文件已修改，是否保存更改？')
            if response is None:  # 取消
                return
            elif response:  # 是
                self.save_file()
        
        # 使用文件对话框，支持选择.dat和.json文件
        file_path = filedialog.askopenfilename(
            title='选择存档文件',
            filetypes=[('存档文件', '*.dat'), ('JSON文件', '*.json'), ('所有文件', '*.*')]
        )
        
        if not file_path:
            return
        
        try:
            # 根据文件扩展名决定如何加载
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext == '.dat':
                # 使用decode.py中的逻辑处理.dat文件
                with open(file_path, 'rb') as f:
                    data = f.read()
                
                # 移除头部
                data = self.remove_header(data)
                
                # 解密数据
                result = self.decrypt_data(data)
                if not result:
                    raise Exception('解密失败')
                
                self.data = json.loads(result)
            else:
                # 普通JSON文件
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            
            self.file_path = file_path
            self.modified = False
            self.status_var.set(f'已加载: {os.path.basename(file_path)}')
            
            # 清空树形视图
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # 填充树形视图
            self.populate_tree('', self.data)
            
        except Exception as e:
            messagebox.showerror('错误', f'无法加载文件: {str(e)}')
    
    def save_file(self):
        if not self.file_path or not self.data:
            messagebox.showwarning('警告', '没有加载文件')
            return
        
        if not self.modified:
            messagebox.showinfo('信息', '文件未修改，无需保存')
            return
        
        try:
            # 创建备份
            backup_dir = os.path.join(os.path.dirname(self.file_path), 'backups')
            os.makedirs(backup_dir, exist_ok=True)
            
            backup_name = f"{os.path.basename(self.file_path)}.{datetime.now().strftime('%Y%m%d%H%M%S')}.bak"
            backup_path = os.path.join(backup_dir, backup_name)
            
            shutil.copy2(self.file_path, backup_path)
            
            # 根据文件扩展名决定如何保存
            ext = os.path.splitext(self.file_path)[1].lower()
            
            if ext == '.dat':
                # 将数据转换为JSON字符串
                json_str = json.dumps(self.data, ensure_ascii=False)
                
                # 加密数据
                encrypted_data = self.encrypt_data(json_str)
                if not encrypted_data:
                    raise Exception('加密失败')
                
                # 保存为二进制文件
                with open(self.file_path, 'wb') as f:
                    f.write(encrypted_data)
            else:
                # 普通JSON文件
                with open(self.file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.data, f, ensure_ascii=False, indent=2)
            
            # 同时保存一份user1.dat文件到游戏目录，确保游戏能读取
            game_dat_path = os.path.join(os.path.dirname(self.file_path), 'user1.dat')
            json_str = json.dumps(self.data, ensure_ascii=False)
            encrypted_data = self.encrypt_data(json_str)
            if encrypted_data:
                with open(game_dat_path, 'wb') as f:
                    f.write(encrypted_data)
                self.status_var.set(f'已保存: {os.path.basename(self.file_path)}, 备份至: {backup_name}, 同时更新游戏存档')
                messagebox.showinfo('成功', f'文件已保存，备份至: {backup_path}\n同时已更新游戏存档: {game_dat_path}')
            else:
                self.modified = False
                self.status_var.set(f'已保存: {os.path.basename(self.file_path)}, 备份至: {backup_name}')
                messagebox.showinfo('成功', f'文件已保存，备份至: {backup_path}\n但更新游戏存档失败')
            
            self.modified = False
            
        except Exception as e:
            messagebox.showerror('错误', f'保存文件时出错: {str(e)}')
            
    def save_as_game_file(self):
        """直接将当前数据保存为游戏可读取的.dat文件"""
        if not self.data:
            messagebox.showwarning('警告', '没有加载文件')
            return
        
        try:
            # 使用文件对话框选择保存位置
            file_path = filedialog.asksaveasfilename(
                title='保存为游戏存档',
                defaultextension='.dat',
                filetypes=[('游戏存档', '*.dat')],
                initialfile='user1.dat'
            )
            
            if not file_path:
                return
            
            # 将数据转换为JSON字符串
            json_str = json.dumps(self.data, ensure_ascii=False)
            
            # 加密数据
            encrypted_data = self.encrypt_data(json_str)
            if not encrypted_data:
                raise Exception('加密失败')
            
            # 保存为二进制文件
            with open(file_path, 'wb') as f:
                f.write(encrypted_data)
            
            self.status_var.set(f'已保存游戏存档: {os.path.basename(file_path)}')
            messagebox.showinfo('成功', f'游戏存档已保存至: {file_path}')
            
        except Exception as e:
            messagebox.showerror('错误', f'保存游戏存档时出错: {str(e)}')
    
    def populate_tree(self, parent, data, key=''):
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
        path = []
        while item != '':
            path.insert(0, self.tree.item(item, 'text'))
            item = self.tree.parent(item)
        # 移除根节点
        if path and path[0] == '':
            path.pop(0)
        return path

    def get_value_from_path(self, data, path):
        print(f"get_value_from_path - 路径: {path}")
        current = data
        for key in path:
            print(f"获取键: {key}, current类型: {type(current)}")
            if key.endswith(' [列表]'):
                key = key[:-6]
                print(f"处理列表键，去除后缀: {key}")
            if isinstance(current, dict):
                print(f"current是字典，键: {list(current.keys())[:5]}...")
                if key not in current:
                    print(f"键 {key} 不存在于字典中")
                    return None
                current = current[key]
                print(f"获取字典值后，current: {current}")
            elif isinstance(current, list):
                print(f"current是列表，长度: {len(current)}")
                try:
                    idx = int(key)
                    if idx >= len(current):
                        print(f"列表索引 {idx} 超出范围 {len(current)}")
                        return None
                    current = current[idx]
                    print(f"获取列表值后，current: {current}")
                except (ValueError, IndexError):
                    print(f"无效的列表索引: {key}")
                    return None
            else:
                print(f"current不是容器类型，而是 {type(current)}")
                return None
        print(f"最终值: {current}, 类型: {type(current)}")
        return current

    def set_value_from_path(self, data, path, value):
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
                            
                        print(f"直接更新{field_name}值为: {data['playerData'][field_name]}")
                        return True
                    except (ValueError, TypeError) as e:
                        messagebox.showerror('错误', f'更新 "{field_name}" 时出错: {str(e)}')
                        return False
        
        # 处理一般情况
        current = data
        path_copy = path.copy()  # 创建路径的副本，避免修改原始路径
        parent_objects = []  # 存储路径上的所有对象
        parent_keys = []     # 存储对应的键或索引
        
        # 处理最后一个键之前的路径
        while len(path_copy) > 1:
            key = path_copy.pop(0)
            parent_objects.append(current)  # 保存当前对象
            
            if key.endswith(' [列表]'):
                key = key[:-6]
                
            parent_keys.append(key)  # 保存当前键
                
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
        selected = self.tree.selection()
        if not selected:
            return

        item = selected[0]
        values = self.tree.item(item, 'values')
        if values:  # 只有叶子节点有值
            self.value_entry.delete(0, tk.END)
            self.value_entry.insert(0, values[0])

    def update_value(self):
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

if __name__ == '__main__':
    root = tk.Tk()
    app = SaveEditor(root)
    root.mainloop()