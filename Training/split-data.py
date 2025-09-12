import os
import shutil
import random
import matplotlib.pyplot as plt

def split_dataset(dataset_dir, output_dir, train_ratio=0.7, val_ratio=0.15, test_ratio=0.15, seed=42):
    random.seed(seed)
    
    # Tạo thư mục output
    for split in ["train", "val", "test"]:
        split_path = os.path.join(output_dir, split)
        os.makedirs(split_path, exist_ok=True)

    # Lặp qua từng lớp
    for class_name in os.listdir(dataset_dir):
        class_path = os.path.join(dataset_dir, class_name)
        if not os.path.isdir(class_path):
            continue

        images = os.listdir(class_path)
        random.shuffle(images)

        n_total = len(images)
        n_train = int(n_total * train_ratio)
        n_val = int(n_total * val_ratio)
        n_test = n_total - n_train - n_val  # phần còn lại

        train_files = images[:n_train]
        val_files = images[n_train:n_train+n_val]
        test_files = images[n_train+n_val:]

        # Copy ảnh sang thư mục mới
        for split, split_files in zip(["train", "val", "test"], [train_files, val_files, test_files]):
            split_class_dir = os.path.join(output_dir, split, class_name)
            os.makedirs(split_class_dir, exist_ok=True)
            for fname in split_files:
                src = os.path.join(class_path, fname)
                dst = os.path.join(split_class_dir, fname)
                shutil.copy2(src, dst)

    print("✅ Done splitting dataset!")


def split_small_subset(dataset_dir, output_dir, subset_ratio=0.1, train_ratio=0.8, seed=42):
    random.seed(seed)

    for split in ["train", "val"]:
        split_path = os.path.join(output_dir, split)
        os.makedirs(split_path, exist_ok=True)

    for class_name in os.listdir(dataset_dir):
        class_path = os.path.join(dataset_dir, class_name)
        if not os.path.isdir(class_path):
            continue

        images = os.listdir(class_path)
        random.shuffle(images)

        # Lấy 20% ảnh
        n_subset = int(len(images) * subset_ratio)
        subset_images = images[:n_subset]

        # Chia tiếp train/val
        n_train = int(n_subset * train_ratio)
        train_files = subset_images[:n_train]
        val_files = subset_images[n_train:]

        # Copy sang thư mục mới
        for split, split_files in zip(["train", "val"], [train_files, val_files]):
            split_class_dir = os.path.join(output_dir, split, class_name)
            os.makedirs(split_class_dir, exist_ok=True)
            for fname in split_files:
                src = os.path.join(class_path, fname)
                dst = os.path.join(split_class_dir, fname)
                shutil.copy2(src, dst)

    print("✅ Done splitting subset dataset!")



def plot_dataset_distribution(output_dir):
    splits = ["train", "val", "test"]
    distribution = {}

    for split in splits:
        split_dir = os.path.join(output_dir, split)
        class_counts = {}
        for class_name in os.listdir(split_dir):
            class_path = os.path.join(split_dir, class_name)
            if os.path.isdir(class_path):
                count = len(os.listdir(class_path))
                class_counts[class_name] = count
        distribution[split] = class_counts

    # Vẽ biểu đồ
    classes = sorted(list(distribution["train"].keys()))
    x = range(len(classes))

    plt.figure(figsize=(12, 6))

    bar_width = 0.25
    plt.bar([i - bar_width for i in x],
            [distribution["train"][c] for c in classes],
            width=bar_width, label="Train")

    plt.bar(x,
            [distribution["val"][c] for c in classes],
            width=bar_width, label="Validation")

    plt.bar([i + bar_width for i in x],
            [distribution["test"][c] for c in classes],
            width=bar_width, label="Test")

    plt.xticks(x, classes, rotation=45)
    plt.ylabel("Số lượng ảnh")
    plt.title("Phân bố ảnh trong Train/Val/Test")
    plt.legend()
    plt.tight_layout()
    plt.show()


def plot_dataset_distribution_subnet(output_dir):
    splits = ["train", "val"]
    distribution = {}

    for split in splits:
        split_dir = os.path.join(output_dir, split)
        class_counts = {}
        for class_name in os.listdir(split_dir):
            class_path = os.path.join(split_dir, class_name)
            if os.path.isdir(class_path):
                count = len(os.listdir(class_path))
                class_counts[class_name] = count
        distribution[split] = class_counts

    # Vẽ biểu đồ
    classes = sorted(list(distribution["train"].keys()))
    x = range(len(classes))

    plt.figure(figsize=(12, 6))

    bar_width = 0.25
    plt.bar([i - bar_width for i in x],
            [distribution["train"][c] for c in classes],
            width=bar_width, label="Train")

    plt.bar(x,
            [distribution["val"][c] for c in classes],
            width=bar_width, label="Validation")


    plt.xticks(x, classes, rotation=45)
    plt.ylabel("Số lượng ảnh")
    plt.title("Phân bố ảnh trong Train/Val")
    plt.legend()
    plt.tight_layout()
    plt.show()



if __name__ == "__main__":

    dataset_dir = "E:/dataset-plant"          
    output_dir = "E:/dataset-plant-split"     
    # split_dataset(dataset_dir, output_dir)
    # plot_dataset_distribution(output_dir)

    output_subnet_dir = "E:/dataset-plant-subset"    
    split_small_subset(dataset_dir, output_subnet_dir)
    plot_dataset_distribution_subnet(output_subnet_dir)
