import os
import random

def merge_and_shuffle_jsonl(target_dirs, output_file):
    """
    Gộp tất cả các file .jsonl từ các thư mục con, trộn ngẫu nhiên các dòng,
    và ghi ra một file đầu ra duy nhất.

    Args:
        target_dirs (list): Danh sách tên các thư mục cần quét.
        output_file (str): Tên của file .jsonl đầu ra.
    """
    all_lines = []
    total_files_processed = 0
    
    print("--- Bắt đầu quá trình gộp file ---")

    # Bước 1: Đọc và tập hợp tất cả các dòng từ các file
    for subdir in target_dirs:
        if not os.path.isdir(subdir):
            print(f"\nCảnh báo: Thư mục '{subdir}' không tồn tại. Bỏ qua.")
            continue

        print(f"\nĐang quét thư mục: '{subdir}'")
        
        for filename in os.listdir(subdir):
            if filename.endswith('.jsonl'):
                total_files_processed += 1
                file_path = os.path.join(subdir, filename)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        # Đọc các dòng và loại bỏ các dòng trống (nếu có)
                        lines = [line for line in f if line.strip()]
                        all_lines.extend(lines)
                        print(f"  - Đã đọc {len(lines)} dòng từ file: {filename}")
                except Exception as e:
                    print(f"  - Lỗi khi đọc file {file_path}: {e}")

    total_lines_read = len(all_lines)
    print("\n" + "="*50)
    print(f"Đã đọc xong {total_files_processed} file với tổng cộng {total_lines_read} dòng.")

    # Bước 2: Trộn (shuffle) tất cả các dòng đã thu thập
    if all_lines:
        print("Bắt đầu trộn ngẫu nhiên dữ liệu...")
        random.shuffle(all_lines)
        print("Trộn dữ liệu thành công!")

        # Bước 3: Ghi các dòng đã trộn vào file đầu ra
        print(f"Đang ghi dữ liệu đã trộn vào file '{output_file}'...")
        try:
            with open(output_file, 'w', encoding='utf-8') as f_out:
                f_out.writelines(all_lines)
            print("\n--- HOÀN TẤT ---")
            print(f"Đã tạo file '{output_file}' với {len(all_lines)} dòng đã được trộn ngẫu nhiên.")
        except Exception as e:
            print(f"Lỗi khi ghi file đầu ra: {e}")
    else:
        print("Không tìm thấy dữ liệu để xử lý.")

# --- Phần thực thi chính ---
if __name__ == "__main__":
    # Danh sách các thư mục cần quét
    directories_to_scan = ['plant', 'disease_v2', 'cultivation']
    
    # Tên file đầu ra sau khi gộp và trộn
    output_filename = 'merged_shuffled_data.jsonl'
    
    # Gọi hàm để thực hiện
    merge_and_shuffle_jsonl(directories_to_scan, output_filename)