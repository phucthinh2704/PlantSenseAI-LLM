import json
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib


def visualize_category_distribution(input_file):
    """
    Đọc file .jsonl, đếm số lượng của mỗi category và vẽ biểu đồ cột.
    """
    # 1. Đọc file và đếm category
    print(f"Đang đọc và phân tích file '{input_file}'...")
    categories = []
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            for line_number, line in enumerate(f, 1):
                if line.strip():  # Bỏ qua các dòng trống
                    try:
                        data = json.loads(line)
                        if "category" in data:
                            categories.append(data["category"])
                    except json.JSONDecodeError:
                        # THAY ĐỔI Ở ĐÂY: In ra dòng bị lỗi
                        print(
                            f"Cảnh báo: Bỏ qua dòng {line_number} không phải định dạng JSON. Nội dung: '{line.strip()}'"
                        )
    except FileNotFoundError:
        print(
            f"Lỗi: Không tìm thấy file '{input_file}'. Vui lòng kiểm tra lại tên file."
        )
        return

    if not categories:
        print("Không tìm thấy category nào trong file để phân tích.")
        return

    category_counts = Counter(categories)
    print("Đã đếm xong. Kết quả:", dict(category_counts))

    # 2. Sắp xếp dữ liệu để vẽ biểu đồ cho đẹp
    sorted_items = sorted(
        category_counts.items(), key=lambda item: item[1], reverse=True
    )
    labels = [item[0] for item in sorted_items]
    counts = [item[1] for item in sorted_items]

    # 3. Vẽ biểu đồ
    print("Đang tạo biểu đồ...")

    # Cấu hình font để hiển thị tiếng Việt
    try:
        matplotlib.rcParams["font.family"] = "Arial"
    except:
        print(
            "Cảnh báo: Không tìm thấy font 'Arial', tiêu đề có thể không hiển thị đúng tiếng Việt."
        )
        matplotlib.rcParams["font.family"] = "sans-serif"

    fig, ax = plt.subplots(figsize=(10, 7))

    colors = [
        "#2E8B57",
        "#DC143C",
        "#FF8C00",
    ]  # Xanh (plant), Đỏ (disease), Cam (cultivation)
    bars = ax.bar(labels, counts, color=colors[: len(labels)])

    # Thêm số lượng trên đầu mỗi cột
    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            f"{height}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=12,
        )

    # Cấu hình cho biểu đồ
    ax.set_ylabel("Số lượng dòng (câu hỏi)", fontsize=12)
    ax.set_title("Sơ đồ Phân bố Dữ liệu theo Category", fontsize=16, pad=20)
    ax.tick_params(axis="x", labelsize=12)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Hiển thị biểu đồ
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    merged_file = "merged_shuffled_data.jsonl"
    visualize_category_distribution(merged_file)
