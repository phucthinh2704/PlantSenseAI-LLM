import random

# --- CẤU HÌNH ---
INPUT_FILE = 'merged_shuffled_data.jsonl'  # Tên file đã gộp và trộn
TRAIN_FILE = 'train.jsonl'
VALIDATION_FILE = 'validation.jsonl'
SPLIT_RATIO = 0.8  # 80% cho training, 20% cho validation

# --- CHƯƠNG TRÌNH ---
def split_data():
    """
    Chia file .jsonl thành hai file train và validation.
    """
    try:
        print(f"Đang đọc dữ liệu từ '{INPUT_FILE}'...")
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Dữ liệu đã được trộn từ bước trước, nên ta không cần trộn lại.
        # Nếu chưa chắc, có thể thêm: random.shuffle(lines)
        
        total_lines = len(lines)
        if total_lines == 0:
            print("Lỗi: File đầu vào không có dữ liệu.")
            return

        # Tính toán điểm chia
        split_point = int(total_lines * SPLIT_RATIO)
        
        # Chia dữ liệu
        train_lines = lines[:split_point]
        validation_lines = lines[split_point:]
        
        print(f"Tổng cộng có {total_lines} dòng.")
        print(f"Chia {len(train_lines)} dòng cho training và {len(validation_lines)} dòng cho validation.")
        
        # Ghi file training
        print(f"Đang ghi file '{TRAIN_FILE}'...")
        with open(TRAIN_FILE, 'w', encoding='utf-8') as f:
            f.writelines(train_lines)
            
        # Ghi file validation
        print(f"Đang ghi file '{VALIDATION_FILE}'...")
        with open(VALIDATION_FILE, 'w', encoding='utf-8') as f:
            f.writelines(validation_lines)
            
        print("\n--- HOÀN TẤT ---")
        print("Đã tạo thành công file training và validation.")
        
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file '{INPUT_FILE}'. Hãy đảm bảo file này tồn tại trong cùng thư mục.")
    except Exception as e:
        print(f"Đã xảy ra lỗi không mong muốn: {e}")

if __name__ == "__main__":
    split_data()