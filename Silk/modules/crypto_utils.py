import base64
import json
from Crypto.Cipher import AES

class CryptoUtils:
    @staticmethod
    def remove_header(data):
        """
        移除C#固定头部和长度前缀
        """
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
            print(f'移除头部时出错: {str(e)}')
            return None
    
    @staticmethod
    def decrypt_data(data):
        """
        解密数据
        """
        try:
            # Base64解码
            decoded = base64.b64decode(data)
            
            # AES解密 (ECB模式)
            key = 'UKu52ePUBwetZ9wNX88o54dnfKRu0T1l'.encode('utf-8')[:32]  # 固定密钥
            cipher = AES.new(key, AES.MODE_ECB)
            decrypted = cipher.decrypt(decoded)
            
            # 移除PKCS7填充
            padding_length = decrypted[-1]
            if padding_length > AES.block_size:
                raise ValueError("Invalid padding")
            for i in range(1, padding_length + 1):
                if decrypted[-i] != padding_length:
                    raise ValueError("Invalid padding")
            unpadded = decrypted[:-padding_length]
            
            # 返回UTF-8字符串
            return unpadded.decode('utf-8')
        except Exception as e:
            print(f'解密失败: {str(e)}')
            return None
    
    @staticmethod
    def encrypt_data(data):
        """
        加密数据
        """
        try:
            # 转换为字节
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            # PKCS7填充
            block_size = AES.block_size
            padding_length = block_size - (len(data) % block_size)
            padded = data + bytes([padding_length] * padding_length)
            
            # AES加密 (ECB模式)
            key = 'UKu52ePUBwetZ9wNX88o54dnfKRu0T1l'.encode('utf-8')[:32]  # 固定密钥
            cipher = AES.new(key, AES.MODE_ECB)
            encrypted = cipher.encrypt(padded)
            
            # Base64编码
            encoded = base64.b64encode(encrypted)
            
            # 添加头部
            return CryptoUtils.add_header(encoded)
        except Exception as e:
            print(f'加密失败: {str(e)}')
            return None
    
    @staticmethod
    def generate_length_prefixed_string(length):
        """
        生成带长度前缀的字符串
        """
        result = bytearray()
        
        # 7-bit encoded int
        while True:
            # Get 7 bits
            value = length & 0x7F
            length >>= 7
            
            if length > 0:
                # Set the high bit
                value |= 0x80
            
            result.append(value)
            
            if length == 0:
                break
        
        return bytes(result)
    
    @staticmethod
    def add_header(data):
        """
        添加C#固定头部和长度前缀
        """
        # C# fixed header
        csharp_header = bytes([0, 1, 0, 0, 0, 255, 255, 255, 255, 1, 0, 0, 0, 0, 0, 0, 0, 6, 1, 0, 0, 0])
        
        # Generate LengthPrefixedString header
        length_data = CryptoUtils.generate_length_prefixed_string(len(data))
        
        # Combine all parts
        result = bytearray(csharp_header)
        result.extend(length_data)
        result.extend(data)
        result.append(11)  # fixed ending byte
        
        return bytes(result)