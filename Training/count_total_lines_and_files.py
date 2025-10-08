import os

def count_stats_in_subdirs(target_dirs):
    """
    Đếm tổng số file và tổng số dòng của các file .jsonl trong danh sách các thư mục con được chỉ định.

    Args:
        target_dirs (list): Danh sách tên các thư mục cần quét.

    Returns:
        tuple: (tổng số file, tổng số dòng)
    """
    grand_total_lines = 0
    grand_total_files = 0

    print("--- Bắt đầu quét các thư mục ---")

    # Lặp qua từng thư mục con trong danh sách
    for subdir in target_dirs:
        # Kiểm tra xem thư mục có tồn tại không
        if not os.path.isdir(subdir):
            print(f"\nCảnh báo: Thư mục '{subdir}' không tồn tại. Bỏ qua.")
            continue

        print(f"\nĐang quét thư mục: '{subdir}'")
        dir_total_lines = 0
        dir_total_files = 0
        
        # Lặp qua từng file trong thư mục con
        for filename in os.listdir(subdir):
            # Chỉ xử lý các file .jsonl
            if filename.endswith('.jsonl'):
                grand_total_files += 1
                dir_total_files += 1
                
                file_path = os.path.join(subdir, filename)
                
                try:
                    # Mở và đếm số dòng
                    with open(file_path, 'r', encoding='utf-8') as f:
                        line_count = sum(1 for line in f)
                        print(f"  - File: {filename}, Số dòng: {line_count}")
                        grand_total_lines += line_count
                        dir_total_lines += line_count
                except Exception as e:
                    print(f"  - Lỗi khi đọc file {file_path}: {e}")

        print(f"-> Tổng cộng cho '{subdir}': {dir_total_files} file, {dir_total_lines} dòng.")

    print("\n" + "="*25 + " TỔNG KẾT " + "="*25)
    return grand_total_files, grand_total_lines

# --- Phần thực thi chính ---
if __name__ == "__main__":
    # Danh sách các thư mục cần quét, nằm cùng cấp với file .py này
    directories_to_scan = ['plant', 'disease_v2', 'cultivation']
    
    # Gọi hàm và nhận kết quả
    total_files, total_lines = count_stats_in_subdirs(directories_to_scan)
    
    # In kết quả tổng cuối cùng
    print(f"\nTổng số file .jsonl trong tất cả các thư mục: {total_files}")
    print(f"Tổng số dòng trong tất cả các file .jsonl: {total_lines}")