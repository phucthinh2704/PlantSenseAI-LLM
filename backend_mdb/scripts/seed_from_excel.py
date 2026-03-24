import os
import sys
import pandas as pd
from dotenv import load_dotenv
import asyncio
from datetime import datetime, timezone

# Add root folder to sys.path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import db

load_dotenv()

async def process_and_seed_excel(file_path: str):
    print("Đang đọc dữ liệu từ Excel...")
    
    # 1. Đọc Sheet 1: Danh mục giống cây
    df_cat = pd.read_excel(file_path, sheet_name=0)
    # THÊM DÒNG NÀY: Chỉ lấy 5 cột đầu tiên, bỏ qua các cột rác phía sau
    df_cat = df_cat.iloc[:, :5] 
    df_cat.columns = ['ID', 'Taxonomy', 'Species', 'No_Varieties', 'Variety']
    df_cat['Taxonomy'] = df_cat['Taxonomy'].ffill()
    df_cat['Species'] = df_cat['Species'].ffill()
    df_cat = df_cat.dropna(subset=['Variety']) # Bỏ dòng không có tên giống
    
    # Tạo dictionary để tra cứu Category và Species dựa vào tên giống
    taxonomy_map = {}
    for _, row in df_cat.iterrows():
        variety = str(row['Variety']).strip()
        taxonomy_map[variety] = {
            "category": str(row['Taxonomy']).strip(),
            "plant_type": str(row['Species']).strip()
        }

    # 2. Đọc Sheet 2: Thông tin loài
    df_info = pd.read_excel(file_path, sheet_name=1)
    # THÊM DÒNG NÀY: Chỉ lấy 7 cột đầu tiên
    df_info = df_info.iloc[:, :7]
    df_info.columns = ['Intro', 'Cat', 'Species', 'Variety', 'Note', 'Reference', 'Image']
    df_info['Variety'] = df_info['Variety'].ffill()
    
    info_map = {}
    for _, row in df_info.iterrows():
        if pd.isna(row['Variety']): continue
        variety = str(row['Variety']).strip()
        
        sources = []
        if pd.notna(row['Reference']):
            refs = str(row['Reference']).split('\n')
            for ref in refs:
                ref = ref.strip()
                if ref:
                    sources.append({"name": "Tài liệu tham khảo", "url": ref, "retrieved_at": datetime.now(timezone.utc).isoformat()})
        
        info_map[variety] = {
            "note": str(row['Note']).strip() if pd.notna(row['Note']) else "",
            "sources": sources
        }

    # 3. Đọc Sheet 3: Thông tin giống & Canh tác
    df_tech = pd.read_excel(file_path, sheet_name=2)
    # THÊM DÒNG NÀY: Chỉ lấy 4 cột đầu tiên
    df_tech = df_tech.iloc[:, :4]
    df_tech.columns = ['Species', 'Variety', 'Variety_Info', 'Cultivation_Info']
    
    plants_to_insert = []
    cultivations_to_insert = []
    
    print("Đang xử lý và map dữ liệu...")
    now = datetime.now(timezone.utc)
    
    for _, row in df_tech.iterrows():
        if pd.isna(row['Variety']): continue
        variety = str(row['Variety']).strip()
        
        # Kết hợp thông tin từ 3 sheet
        tax_info = taxonomy_map.get(variety, {"category": "Không rõ", "plant_type": "Không rõ"})
        extra_info = info_map.get(variety, {"note": "", "sources": []})
        
        variety_info_text = str(row['Variety_Info']).strip() if pd.notna(row['Variety_Info']) else ""
        cultivation_text = str(row['Cultivation_Info']).strip() if pd.notna(row['Cultivation_Info']) else ""
        
        # Gộp chú thích (Sheet 2) và Thông tin giống (Sheet 3) thành Description
        full_description = f"{extra_info['note']}\n{variety_info_text}".strip()

        # Tạo dict Plant
        plant_doc = {
            "name": variety,
            "category": tax_info["category"],
            "plant_type": tax_info["plant_type"],
            "description": full_description,
            "sources": extra_info["sources"],
            "created_at": now,
            "updated_at": now
        }
        plants_to_insert.append((variety, plant_doc, cultivation_text))

    # Xóa dữ liệu cũ (Tùy chọn, nếu bạn muốn làm mới hoàn toàn)
    print("Xóa dữ liệu cũ trong collections: plants, cultivation_techniques...")
    await db.plants.delete_many({})
    await db.cultivation_techniques.delete_many({})

    # Lưu vào MongoDB
    print(f"Đang lưu {len(plants_to_insert)} giống cây vào MongoDB...")
    for variety, plant_doc, cultivation_text in plants_to_insert:
        result = await db.plants.insert_one(plant_doc)
        plant_id = str(result.inserted_id)
        
        # Nếu có thông tin kỹ thuật canh tác, lưu vào bảng cultivation_techniques
        if cultivation_text:
            cultivation_doc = {
                "name": f"Kỹ thuật canh tác giống {variety}",
                "plant_ids": [plant_id],
                "description": cultivation_text,
                "category": "Tổng hợp", 
                "application_period": "Toàn bộ chu kỳ",
                "crop_type": plant_doc["plant_type"],
                "steps": [], # Vì Excel đang lưu dạng đoạn văn, ta đưa hết vào description
                "sources": plant_doc["sources"],
                "created_at": now,
                "updated_at": now
            }
            await db.cultivation_techniques.insert_one(cultivation_doc)

    # --- BỔ SUNG: TẠO TÀI LIỆU TỔNG HỢP THEO DANH MỤC ---
    print("Đang tạo các tài liệu tổng hợp danh mục (Category Summaries)...")
    category_groups = {}
    for variety, plant_doc, _ in plants_to_insert:
        cat = plant_doc.get("category", "Khác")
        if cat not in category_groups:
            category_groups[cat] = []
        category_groups[cat].append(variety)

    for cat, varieties in category_groups.items():
        summary_text = f"Danh sách tổng hợp các giống cây thuộc nhóm {cat} bao gồm: " + ", ".join(varieties) + "."
        
        summary_doc = {
            "name": f"Tổng hợp danh mục {cat}",
            "category": cat,
            "plant_type": "Tổng hợp",
            "description": summary_text,
            "sources": [],
            "created_at": now,
            "updated_at": now
        }
        await db.plants.insert_one(summary_doc)
        
    print("Hoàn tất đẩy dữ liệu Excel vào MongoDB!")

if __name__ == "__main__":
    # Đặt file excel của bạn vào thư mục data (ví dụ: data/knowledge.xlsx)
    excel_path = os.path.join("data", "knowledge.xlsx") 
    asyncio.run(process_and_seed_excel(excel_path))