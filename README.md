# 🎮 SilkSong 存档编辑器

## 项目文件结构

```
Silk/
├── modules/               # 核心模块目录
│   ├── __init__.py        # 包初始化文件
│   ├── crypto_utils.py    # 加密解密工具
│   ├── modern_editor_ui.py # 编辑器UI界面
│   ├── extract_keys.py    # 键提取工具
│   └── file_utils.py      # 文件操作工具
├── data/                  # 数据文件目录
│   ├── __init__.py        # 包初始化文件
│   ├── key_example.json   # 示例键配置
│   └── key_type.json      # 键类型配置
├── main.py         # 主程序入口
├── requirements.txt       # 依赖项列表
├── README.md              # 项目说明文档
├── backups/               # 备份文件目录

```
## 使用说明
1. 备份您的原始存档文件
2. 运行dist文件夹中的存档编辑器文件
3. 点击「文件」->「打开」，选择您的存档文件（.dat格式）
4. 点击要修改的值，在右侧输入框中输入新的值，然后点击「更新」按钮
5. 修改完成后，点击「文件」->「保存」保存修改。程序会自动创建备份，并同时更新游戏存档
6. 如果您想将修改后的存档保存到其他位置，可以点击「文件」->「另存为游戏存档」

## 注意事项

- 在修改存档前，请务必备份原始存档文件
- 不当的修改可能导致游戏无法正常运行或存档损坏
- 本工具仅供学习和研究使用

### 依赖项
- pycryptodome==3.19.0
- tkinter（Python标准库）
- customtkinter>=5.2.2
- darkdetect>=0.8.0

可以通过以下命令安装所有依赖：
```bash
pip install -r requirements.txt
```
