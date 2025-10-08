import os
import json

# Định nghĩa tên file output sau khi merge
output_file = "merged_data.jsonl"

# Lấy thư mục hiện tại (nơi chứa file .py)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Tạo một danh sách chứa các file JSONL trong thư mục
jsonl_files = [f for f in os.listdir(current_dir) if f.endswith(".jsonl")]

# Mở file output để ghi dữ liệu gộp
with open(output_file, 'w', encoding='utf-8') as outfile:
    # Duyệt qua các file JSONL
    for jsonl_file in jsonl_files:
        file_path = os.path.join(current_dir, jsonl_file)
        
        # Mở và đọc từng file JSONL
        with open(file_path, 'r', encoding='utf-8') as infile:
            # Đọc từng dòng (mỗi dòng là một đối tượng JSON)
            for line in infile:
                # Ghi mỗi dòng vào file output
                outfile.write(line)

print(f"Đã merge các file JSONL thành công vào {output_file}")
