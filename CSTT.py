import os
from pathlib import Path
from PIL import Image
import struct
import zlib
import base64
import json
from opencc import OpenCC

class PNGBatchConverter:
    def __init__(self):
        self.cc = OpenCC('s2t')
        self.ensure_folders()
    
    def ensure_folders(self):
        """確保 original 和 translated 資料夾存在"""
        Path("original").mkdir(exist_ok=True)
        Path("translated").mkdir(exist_ok=True)
    
    def try_decode_base64(self, text):
        """嘗試解碼Base64文本"""
        try:
            # 檢查是否看起來像Base64
            if len(text) % 4 == 0 and all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=' for c in text):
                decoded = base64.b64decode(text).decode('utf-8', errors='ignore')
                # 驗證解碼結果是否為有效的中文
                if any('\u4e00' <= c <= '\u9fff' for c in decoded):
                    return decoded
        except:
            pass
        return text
    
    def convert_chunk(self, chunk_type, chunk_data):
        """轉換單個chunk"""
        try:
            if chunk_type == 'tEXt':
                null_pos = chunk_data.find(b'\x00')
                keyword = chunk_data[:null_pos]
                text = chunk_data[null_pos+1:].decode('utf-8', errors='ignore')
                
                decoded_text = self.try_decode_base64(text)
                converted_text = self.cc.convert(decoded_text)
                # 如果原始是Base64，轉換後也編碼為Base64
                if decoded_text != text:
                    final_text = base64.b64encode(converted_text.encode('utf-8')).decode('ascii')
                else:
                    final_text = converted_text
                
                return keyword + b'\x00' + final_text.encode('utf-8')
            
            elif chunk_type == 'zTXt':
                null_pos = chunk_data.find(b'\x00')
                keyword = chunk_data[:null_pos]
                compression = bytes([chunk_data[null_pos+1]])
                compressed_text = chunk_data[null_pos+2:]
                text = zlib.decompress(compressed_text).decode('utf-8', errors='ignore')
                
                decoded_text = self.try_decode_base64(text)
                converted_text = self.cc.convert(decoded_text)
                # 如果原始是Base64，轉換後也編碼為Base64
                if decoded_text != text:
                    final_text = base64.b64encode(converted_text.encode('utf-8')).decode('ascii')
                else:
                    final_text = converted_text
                
                new_compressed = zlib.compress(final_text.encode('utf-8'))
                return keyword + b'\x00' + compression + new_compressed
            
            elif chunk_type == 'iTXt':
                null_pos = chunk_data.find(b'\x00')
                keyword = chunk_data[:null_pos]
                rest = chunk_data[null_pos+1:]
                try:
                    text = rest.decode('utf-8', errors='ignore')
                    
                    decoded_text = self.try_decode_base64(text)
                    converted_text = self.cc.convert(decoded_text)
                    # 如果原始是Base64，轉換後也編碼為Base64
                    if decoded_text != text:
                        final_text = base64.b64encode(converted_text.encode('utf-8')).decode('ascii')
                    else:
                        final_text = converted_text
                    
                    return keyword + b'\x00' + final_text.encode('utf-8')
                except:
                    return chunk_data
        except:
            return chunk_data
        
        return chunk_data
    
    def convert_file(self, input_path, output_path):
        """轉換單個PNG文件"""
        try:
            # 讀取原始PNG
            with open(input_path, 'rb') as f:
                data = f.read()
            
            # 驗證PNG簽名
            if data[:8] != b'\x89PNG\r\n\x1a\n':
                print(f"❌ 跳過 {input_path}: 不是有效的PNG文件")
                return False
            
            # 處理chunks
            output_data = bytearray(data[:8])  # PNG簽名
            pos = 8
            
            while pos < len(data):
                length = struct.unpack('>I', data[pos:pos+4])[0]
                chunk_type = data[pos+4:pos+8]
                chunk_type_str = chunk_type.decode('ascii', errors='ignore')
                chunk_data = data[pos+8:pos+8+length]
                crc = data[pos+8+length:pos+12+length]
                
                # 轉換文本塊
                if chunk_type_str in ['tEXt', 'zTXt', 'iTXt']:
                    chunk_data = self.convert_chunk(chunk_type_str, chunk_data)
                    # 重新計算CRC
                    crc = struct.pack('>I', zlib.crc32(chunk_type + chunk_data) & 0xffffffff)
                
                # 寫入轉換後的chunk
                output_data.extend(struct.pack('>I', len(chunk_data)))
                output_data.extend(chunk_type)
                output_data.extend(chunk_data)
                output_data.extend(crc)
                
                pos += 12 + length
            
            # 保存轉換後的PNG
            with open(output_path, 'wb') as f:
                f.write(output_data)
            
            print(f"✓ 已轉換: {os.path.basename(input_path)} -> {output_path}")
            return True
        
        except Exception as e:
            print(f"❌ 轉換失敗 {input_path}: {str(e)}")
            return False
    
    def convert_json_value(self, value):
        """遞歸轉換 JSON 中的所有字符串值"""
        if isinstance(value, str):
            return self.cc.convert(value)
        elif isinstance(value, dict):
            return {key: self.convert_json_value(val) for key, val in value.items()}
        elif isinstance(value, list):
            return [self.convert_json_value(item) for item in value]
        else:
            return value
    
    def convert_json_file(self, input_path, output_path):
        """轉換單個 JSON 文件"""
        try:
            # 讀取 JSON 文件
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 轉換所有字符串值
            converted_data = self.convert_json_value(data)
            
            # 保存轉換後的 JSON
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(converted_data, f, ensure_ascii=False, indent=2)
            
            print(f"✓ 已轉換: {os.path.basename(input_path)} -> {output_path}")
            return True
        
        except Exception as e:
            print(f"❌ 轉換失敗 {input_path}: {str(e)}")
            return False
    
    def batch_convert(self):
        """批量轉換 original 資料夾中的所有 PNG 和 JSON 文件"""
        original_dir = Path("original")
        translated_dir = Path("translated")
        
        # 獲取所有 PNG 和 JSON 文件
        png_files = list(original_dir.glob("*.png"))
        json_files = list(original_dir.glob("*.json"))
        
        if not png_files and not json_files:
            print("⚠️  original 資料夾中沒有找到 PNG 或 JSON 文件")
            return
        
        total_files = len(png_files) + len(json_files)
        print(f"找到 {len(png_files)} 個 PNG 文件和 {len(json_files)} 個 JSON 文件，開始轉換...\n")
        
        success_count = 0
        fail_count = 0
        
        # 轉換 PNG 文件
        if png_files:
            print("=== 轉換 PNG 文件 ===")
            for png_file in png_files:
                output_path = translated_dir / png_file.name
                if self.convert_file(png_file, output_path):
                    success_count += 1
                else:
                    fail_count += 1
            print()
        
        # 轉換 JSON 文件
        if json_files:
            print("=== 轉換 JSON 文件 ===")
            for json_file in json_files:
                output_path = translated_dir / json_file.name
                if self.convert_json_file(json_file, output_path):
                    success_count += 1
                else:
                    fail_count += 1
            print()
        
        print(f"轉換完成！")
        print(f"成功: {success_count} 個")
        print(f"失敗: {fail_count} 個")

if __name__ == "__main__":
    converter = PNGBatchConverter()
    converter.batch_convert()
