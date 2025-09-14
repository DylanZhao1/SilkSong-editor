import os
import json
import shutil
from datetime import datetime
from tkinter import filedialog, messagebox
from .crypto_utils import CryptoUtils

class FileUtils:
    def __init__(self, status_callback=None):
        """
        初始化文件工具类
        
        参数:
            status_callback: 状态更新回调函数
        """
        self.status_callback = status_callback
    
    def load_file(self, file_path=None):
        """
        加载文件，支持.dat和.json格式
        
        参数:
            file_path: 文件路径，如果为None则弹出文件选择对话框
            
        返回:
            (data, file_path): 加载的数据和文件路径
        """
        # 获取项目根目录和数据目录
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(project_root, 'data')
        
        # 如果没有提供文件路径，使用文件对话框选择
        if not file_path:
            file_path = filedialog.askopenfilename(
                title='选择存档文件',
                initialdir=project_root,
                filetypes=[('存档文件', '*.dat'), ('JSON文件', '*.json'), ('所有文件', '*.*')]
            )
        
        if not file_path:
            return None, None
        
        try:
            # 根据文件扩展名决定如何加载
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext == '.dat':
                # 处理.dat文件
                with open(file_path, 'rb') as f:
                    data = f.read()
                
                # 移除头部
                data = CryptoUtils.remove_header(data)
                
                # 解密数据
                result = CryptoUtils.decrypt_data(data)
                if not result:
                    raise Exception('解密失败')
                
                data = json.loads(result)
            else:
                # 普通JSON文件
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            
            if self.status_callback:
                self.status_callback(f'已加载: {os.path.basename(file_path)}')
            
            return data, file_path
            
        except Exception as e:
            messagebox.showerror('错误', f'无法加载文件: {str(e)}')
            return None, None
    
    def save_file(self, data, file_path, update_game_save=True):
        """
        保存文件，支持.dat和.json格式
        
        参数:
            data: 要保存的数据
            file_path: 文件路径
            update_game_save: 是否同时更新游戏存档
            
        返回:
            bool: 是否保存成功
        """
        if not file_path or not data:
            messagebox.showwarning('警告', '没有加载文件')
            return False
        
        try:
            # 获取项目根目录
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            # 创建备份
            backup_dir = os.path.join(project_root, 'backups')
            os.makedirs(backup_dir, exist_ok=True)
            
            backup_name = f"{os.path.basename(file_path)}.{datetime.now().strftime('%Y%m%d%H%M%S')}.bak"
            backup_path = os.path.join(backup_dir, backup_name)
            
            if os.path.exists(file_path):
                shutil.copy2(file_path, backup_path)
            
            # 根据文件扩展名决定如何保存
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext == '.dat':
                # 将数据转换为JSON字符串
                json_str = json.dumps(data, ensure_ascii=False)
                
                # 加密数据
                encrypted_data = CryptoUtils.encrypt_data(json_str)
                if not encrypted_data:
                    raise Exception('加密失败')
                
                # 保存为二进制文件
                with open(file_path, 'wb') as f:
                    f.write(encrypted_data)
            else:
                # 普通JSON文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            
            # 同时保存一份user1.dat文件到游戏目录，确保游戏能读取
            success_game_save = False
            if update_game_save:
                game_dat_path = os.path.join(os.path.dirname(file_path), 'user1.dat')
                json_str = json.dumps(data, ensure_ascii=False)
                encrypted_data = CryptoUtils.encrypt_data(json_str)
                if encrypted_data:
                    with open(game_dat_path, 'wb') as f:
                        f.write(encrypted_data)
                    if self.status_callback:
                        self.status_callback(f'已保存: {os.path.basename(file_path)}, 备份至: {backup_name}, 同时更新游戏存档')
                    messagebox.showinfo('成功', f'文件已保存，备份至: {backup_path}\n同时已更新游戏存档: {game_dat_path}')
                    success_game_save = True
            
            if not success_game_save:
                if self.status_callback:
                    self.status_callback(f'已保存: {os.path.basename(file_path)}, 备份至: {backup_name}')
                messagebox.showinfo('成功', f'文件已保存，备份至: {backup_path}')
            
            return True
            
        except Exception as e:
            messagebox.showerror('错误', f'保存文件时出错: {str(e)}')
            return False
    
    def save_as_game_file(self, data):
        """
        将数据保存为游戏可读取的.dat文件
        
        参数:
            data: 要保存的数据
            
        返回:
            bool: 是否保存成功
        """
        if not data:
            messagebox.showwarning('警告', '没有加载文件')
            return False
        
        try:
            # 使用文件对话框选择保存位置
            file_path = filedialog.asksaveasfilename(
                title='保存为游戏存档',
                defaultextension='.dat',
                filetypes=[('游戏存档', '*.dat')],
                initialfile='user1.dat'
            )
            
            if not file_path:
                return False
            
            # 将数据转换为JSON字符串
            json_str = json.dumps(data, ensure_ascii=False)
            
            # 加密数据
            encrypted_data = CryptoUtils.encrypt_data(json_str)
            if not encrypted_data:
                raise Exception('加密失败')
            
            # 保存为二进制文件
            with open(file_path, 'wb') as f:
                f.write(encrypted_data)
            
            if self.status_callback:
                self.status_callback(f'已保存游戏存档: {os.path.basename(file_path)}')
            messagebox.showinfo('成功', f'游戏存档已保存至: {file_path}')
            return True
            
        except Exception as e:
            messagebox.showerror('错误', f'保存游戏存档时出错: {str(e)}')
            return False