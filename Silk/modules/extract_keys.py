import os
import json
from .crypto_utils import CryptoUtils

def extract_keys(data, prefix='', result=None):
    """
    递归提取JSON数据中的所有键
    
    参数:
        data: 要提取键的数据
        prefix: 当前键的前缀
        result: 结果字典
        
    返回:
        dict: 包含所有键的字典
    """
    if result is None:
        result = {}
    
    if isinstance(data, dict):
        for key, value in data.items():
            current_key = f"{prefix}.{key}" if prefix else key
            result[current_key] = type(value).__name__
            extract_keys(value, current_key, result)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            current_key = f"{prefix}[{i}]"
            result[current_key] = type(item).__name__
            extract_keys(item, current_key, result)
    
    return result

def main():
    # 获取项目根目录下的所有.dat文件
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dat_files = [f for f in os.listdir(project_root) if f.endswith('.dat')]
    
    if not dat_files:
        print("项目根目录下没有找到.dat文件")
        return
    
    # 确保data目录存在
    data_dir = os.path.join(project_root, 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    for dat_file in dat_files:
        try:
            dat_file_path = os.path.join(project_root, dat_file)
            print(f"处理文件: {dat_file}")
            
            # 读取.dat文件
            with open(dat_file_path, 'rb') as f:
                data = f.read()
            
            # 移除头部
            data = CryptoUtils.remove_header(data)
            
            # 解密数据
            json_str = CryptoUtils.decrypt_data(data)
            if not json_str:
                print(f"解密失败: {dat_file}")
                continue
            
            # 解析JSON
            json_data = json.loads(json_str)
            
            # 提取所有键
            keys = extract_keys(json_data)
            
            # 保存为JSON文件
            base_name = os.path.splitext(os.path.basename(dat_file))[0]
            output_file = os.path.join(data_dir, f"{base_name}_keys.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(keys, f, indent=2, ensure_ascii=False)
            
            print(f"已生成键列表: {output_file}")
            
            # 同时保存完整的JSON数据
            full_json_file = os.path.join(data_dir, f"{base_name}_full.json")
            with open(full_json_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            print(f"已生成完整JSON: {full_json_file}")
            
        except Exception as e:
            print(f"处理文件 {dat_file} 时出错: {str(e)}")

if __name__ == '__main__':
    main()