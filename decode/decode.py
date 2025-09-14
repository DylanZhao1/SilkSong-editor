import base64
from Crypto.Cipher import AES
import json
import os

def remove_header(data):
    try:
        # C# fixed header
        csharp_header = bytes([0, 1, 0, 0, 0, 255, 255, 255, 255, 1, 0, 0, 0, 0, 0, 0, 0, 6, 1, 0, 0, 0])
        log_message = f'Original data length: {len(data)}\n'
        
        # Remove fixed header and ending byte 11
        data = data[len(csharp_header):-1]
        log_message += f'After removing fixed header length: {len(data)}\n'
        
        # Remove LengthPrefixedString header
        length_count = 0
        for i in range(5):
            length_count += 1
            if (data[i] & 0x80) == 0:
                break
        
        data = data[length_count:]
        log_message += f'After removing length prefix length: {len(data)}\n'
        
        with open('decode_log.txt', 'a') as f:
            f.write(log_message)
        return data
    except Exception as e:
        with open('decode_log.txt', 'a') as f:
            f.write(f'Error in remove_header: {str(e)}\n')
        raise

def decrypt_data(data):
    try:
        # Base64 decode
        log_message = f'Data before base64 decode: {len(data)} bytes\n'
        decoded = base64.b64decode(data)
        log_message += f'Data after base64 decode: {len(decoded)} bytes\n'
        
        # AES key
        key = 'UKu52ePUBwetZ9wNX88o54dnfKRu0T1l'.encode('utf-8')[:32]
        log_message += f'AES key length: {len(key)} bytes\n'
        
        # Create AES cipher in ECB mode
        cipher = AES.new(key, AES.MODE_ECB)
        
        # Decrypt
        decrypted = cipher.decrypt(decoded)
        log_message += f'Data after AES decrypt: {len(decrypted)} bytes\n'
        
        # Remove PKCS7 padding
        padding_length = decrypted[-1]
        log_message += f'PKCS7 padding length: {padding_length}\n'
        decrypted = decrypted[:-padding_length]
        
        # Convert to string and parse JSON
        result = decrypted.decode('utf-8')
        log_message += 'Successfully decoded to string\n'
        parsed = json.loads(result)
        log_message += 'Successfully parsed JSON\n'
        
        with open('decode_log.txt', 'a') as f:
            f.write(log_message)
        
        # Write decrypted content to file
        with open('decrypted_content.json', 'w', encoding='utf-8') as f:
            json.dump(parsed, f, indent=2, ensure_ascii=False)
        
        return json.dumps(parsed, indent=2, ensure_ascii=False)
    except Exception as e:
        with open('decode_log.txt', 'a') as f:
            f.write(f'Error in decrypt_data: {str(e)}\n')
        return None

# Clear previous log
with open('decode_log.txt', 'w') as f:
    f.write('Starting decryption process...\n')

# Read the file using absolute path
file_path = os.path.join(os.path.dirname(__file__), 'user1.dat')
with open('decode_log.txt', 'a') as f:
    f.write(f'Reading file: {file_path}\n')

try:
    with open(file_path, 'rb') as f:
        data = f.read()
    with open('decode_log.txt', 'a') as f:
        f.write('Successfully read file\n')

    # Remove headers
    data = remove_header(data)

    # Decrypt and print
    result = decrypt_data(data)
    if result:
        with open('decode_log.txt', 'a') as f:
            f.write('\nDecryption successful\n')
    else:
        with open('decode_log.txt', 'a') as f:
            f.write('Failed to decrypt data\n')
except Exception as e:
    with open('decode_log.txt', 'a') as f:
        f.write(f'Error: {str(e)}\n')