import os

def count_total_lines_jsonl(directory):
    # Khởi tạo biến đếm tổng số dòng
    total_lines = 0
    
    # Lấy danh sách tất cả các file trong thư mục
    for filename in os.listdir(directory):
        # Kiểm tra file có đuôi .jsonl không
        if filename.endswith('.jsonl'):
            file_path = os.path.join(directory, filename)
            try:
                # Đếm số dòng trong file
                with open(file_path, 'r', encoding='utf-8') as file:
                    line_count = sum(1 for line in file)
                    print(f"File: {filename}, Số dòng: {line_count}")
                    total_lines += line_count
            except Exception as e:
                print(f"Lỗi khi đọc file {filename}: {e}")
    
    return total_lines

def count_jsonl_files():
    """
    Đếm tổng số file JSONL (.jsonl) trong thư mục hiện tại.
    
    Returns:
        int: Số lượng file JSONL
        list: Danh sách tên các file JSONL
    """
    try:
        # Lấy đường dẫn thư mục hiện tại
        current_directory = os.getcwd()
        
        # Liệt kê tất cả file trong thư mục
        files = os.listdir(current_directory)
        
        # Lọc các file có đuôi .jsonl
        jsonl_files = [f for f in files if f.endswith('.jsonl')]
        
        # Đếm số lượng file JSONL
        count = len(jsonl_files)
        
        # In kết quả
        print(f"Tổng số file JSONL trong thư mục '{current_directory}': {count}")
        
        return count, jsonl_files
    
    except Exception as e:
        print(f"Lỗi: {str(e)}")
        return 0, []

# Ví dụ sử dụng
    
# Thư mục hiện tại (có thể thay đổi đường dẫn nếu cần)
directory = os.getcwd()

# Gọi hàm và in kết quả
total = count_total_lines_jsonl(directory)
print(f"\nTổng số dòng trong tất cả file JSONL: {total}")

count, jsonl_files = count_jsonl_files()
print(f"Kết quả: Đã tìm thấy {count} file JSONL.")