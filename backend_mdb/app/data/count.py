import json

def count_json_elements(file_path):
    """
    Đếm số phần tử trong file JSON.
    
    Args:
        file_path (str): Đường dẫn đến file JSON
        
    Returns:
        int: Số lượng phần tử trong file JSON
        None: Nếu có lỗi xảy ra
    """
    try:
        # Mở và đọc file JSON
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            
        # Kiểm tra xem dữ liệu có phải là list không
        if not isinstance(data, list):
            print("Lỗi: File JSON không chứa một danh sách (list).")
            return None
            
        # Đếm số phần tử
        count = len(data)
        print(f"Số lượng phần tử trong file JSON: {count}")
        
        # In thông tin cơ bản về các phần tử (tùy chọn)
        for i, item in enumerate(data, 1):
            name = item.get('name', 'Không có tên')
            # print(f"Phần tử {i}: {name}")
            
        return count
    
    except FileNotFoundError:
        print(f"Lỗi: File '{file_path}' không tồn tại.")
        return None
    except json.JSONDecodeError:
        print("Lỗi: File JSON có định dạng không hợp lệ.")
        return None
    except Exception as e:
        print(f"Lỗi không xác định: {str(e)}")
        return None

# Ví dụ sử dụng
if __name__ == "__main__":
    # Thay 'data.json' bằng đường dẫn thực tế đến file JSON của bạn
    file_path = 'plant_data.json'
    
    # Gọi hàm để đếm phần tử
    result = count_json_elements(file_path)
    
    if result is not None:
        print(f"Kết quả: Đã đếm được {result} phần tử.")