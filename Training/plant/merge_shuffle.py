import os
import json
import random

def merge_and_shuffle_jsonl(directory, output_file):
    # Danh sách để lưu tất cả các dòng từ các file JSONL
    all_lines = []
    
    # Duyệt qua tất cả các file trong thư mục
    for filename in os.listdir(directory):
        if filename.endswith('.jsonl'):
            file_path = os.path.join(directory, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    # Đọc từng dòng và thêm vào danh sách
                    for line in file:
                        all_lines.append(line.strip())
                print(f"Đã đọc {filename}: {sum(1 for _ in open(file_path, 'r', encoding='utf-8'))} dòng")
            except Exception as e:
                print(f"Lỗi khi đọc file {filename}: {e}")
    
    # Trộn ngẫu nhiên các dòng
    random.shuffle(all_lines)
    
    # Ghi các dòng đã trộn vào file mới
    try:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            for line in all_lines:
                outfile.write(line + '\n')
        print(f"Đã ghi {len(all_lines)} dòng vào file {output_file}")
    except Exception as e:
        print(f"Lỗi khi ghi file {output_file}: {e}")

# Thư mục hiện tại (có thể thay đổi đường dẫn nếu cần)
directory = os.getcwd()
# Tên file đầu ra
output_file = 'merged_shuffled.jsonl'

# Gọi hàm
merge_and_shuffle_jsonl(directory, output_file)