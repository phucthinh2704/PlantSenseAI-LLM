# indexing.py (Fixed for WriteTimeout issue)

import os
import pymongo
from dotenv import load_dotenv
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
import json
from bson import ObjectId
import pypdf  # Import mới
import docx   # Import mới


# --- 1. TẢI BIẾN MÔI TRƯỜNG & KẾT NỐI ---
load_dotenv()
mongo_client = pymongo.MongoClient(os.getenv("MONGO_URI"))
db = mongo_client[os.getenv("MONGO_DB_NAME")]
COLLECTION_CONFIG = {
    "plant": "plants",
    "disease_stage": "disease_stages",
    "cultivation_technique": "cultivation_techniques",
}

# =================================================================
# === THAY ĐỔI DUY NHẤT NẰM Ở ĐÂY ===
# =================================================================
# Kết nối Qdrant với thời gian chờ (timeout) dài hơn
qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
    timeout=60,  # **SỬA LỖI: Tăng thời gian chờ lên 60 giây**
)
# =================================================================


# --- 2. KHỞI TẠO CÁC MÔ HÌNH ---
print("Đang tải model embedding...")
embedding_model = SentenceTransformer(os.getenv("MODEL_EMBEDDING"))

if hasattr(embedding_model.tokenizer, "model_max_length"):
    embedding_model.max_seq_length = embedding_model.tokenizer.model_max_length
    print(f"Model max sequence length được đặt thành: {embedding_model.max_seq_length}")
else:
    embedding_model.max_seq_length = 512
    print(
        f"Không tìm thấy max length, đặt mặc định an toàn thành: {embedding_model.max_seq_length}"
    )

VECTOR_DIMENSION = embedding_model.get_sentence_embedding_dimension()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
print("Tải model thành công!")


# --- CÁC PHẦN CÒN LẠI CỦA FILE GIỮ NGUYÊN ---

# --- 3. TẠO COLLECTION TRONG QDRANT ---
collection_name = os.getenv("QDRANT_COLLECTION_NAME")
try:
    qdrant_client.get_collection(collection_name=collection_name)
    print(f"Collection '{collection_name}' đã tồn tại.")
except Exception:
    print(f"Collection '{collection_name}' chưa tồn tại. Đang tạo mới...")
    qdrant_client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(
            size=VECTOR_DIMENSION, distance=models.Distance.COSINE
        ),
    )
    print("Tạo collection thành công!")


# --- 4. CÁC HÀM FORMAT ---
def format_plant_document_to_text(
    doc: dict, db_client: pymongo.database.Database
) -> str:
    parts = []
    if doc.get("name"):
        parts.append(f"Tên giống cây: {doc['name']}.")
    if doc.get("plant_type"):
        parts.append(f"Loại cây: {doc['plant_type']}.")
    if doc.get("category"):
        parts.append(f"Phân loại: {doc['category']}.")
    if doc.get("origin"):
        parts.append(f"Nguồn gốc: {doc['origin']}.")
    if doc.get("growth_duration"):
        parts.append(f"Thời gian sinh trưởng: {doc['growth_duration']}.")
    if doc.get("yields"):
        parts.append(f"Năng suất: {doc['yields']}.")
    if doc.get("morphology"):
        parts.append(f"Đặc điểm hình thái: {doc['morphology']}.")
    if doc.get("description"):
        parts.append(f"Mô tả chi tiết: {doc['description']}.")
    return "\n".join(parts)


def format_disease_stage_document_to_text(
    doc: dict, db_client: pymongo.database.Database
) -> str:
    parts = []
    disease_collection = db_client["diseases"]
    disease_doc = disease_collection.find_one({"_id": ObjectId(doc.get("disease_id"))})
    disease_name = disease_doc.get("name", "Không rõ") if disease_doc else "Không rõ"
    disease_cause = (
        disease_doc.get("cause", "Chưa rõ nguyên nhân")
        if disease_doc
        else "Chưa rõ nguyên nhân"
    )
    parts.append(f"Thông tin về bệnh: {disease_name}.")
    parts.append(f"Nguyên nhân gây bệnh: {disease_cause}.")
    if doc.get("stage"):
        parts.append(f"Giai đoạn: {doc['stage']}.")
    if doc.get("symptom"):
        parts.append(f"Triệu chứng bệnh {disease_name}: {doc['symptom']}.")

    def format_treatment_steps(steps: list, title: str) -> str:
        if not steps:
            return ""
        step_texts = [f"{title}:"]
        for step in steps:
            step_desc = f"- Bước {step.get('step', '')}: {step.get('name', '')}. Mô tả: {step.get('description', '')}."
            if step.get("chemical"):
                step_desc += f" Hoạt chất/Thuốc đề nghị: {step['chemical']}."
            if step.get("dosage"):
                step_desc += f" Liều lượng: {step['dosage']}."
            if step.get("note"):
                step_desc += f" Lưu ý: {step['note']}."
            step_texts.append(step_desc)
        return "\n".join(step_texts)

    parts.append(
        format_treatment_steps(doc.get("prevention", []), f"Biện pháp phòng chống và ngừa bệnh {disease_name}")
    )
    parts.append(format_treatment_steps(doc.get("treatment", []), f"Biện pháp điều trị khi nhiễm bệnh {disease_name}"))
    return "\n".join(filter(None, parts))


def format_cultivation_technique_document_to_text(
    doc: dict, db_client: pymongo.database.Database
) -> str:
    parts = []
    if doc.get("name"):
        parts.append(f"Tên kỹ thuật canh tác: {doc['name']}.")
    if doc.get("crop_type"):
        parts.append(f"Áp dụng cho: {doc['crop_type']}.")
    if doc.get("category"):
        parts.append(f"Phân loại kỹ thuật: {doc['category']}.")
    if doc.get("application_period"):
        parts.append(f"Giai đoạn áp dụng: {doc['application_period']}.")
    if doc.get("description"):
        parts.append(f"Mô tả: {doc['description']}.")
    if doc.get("requirements"):
        parts.append(f"Yêu cầu: {doc['requirements']}.")
    if doc.get("benefits"):
        parts.append(f"Lợi ích: {doc['benefits']}.")
    if doc.get("steps"):
        tech_steps = ["Các bước thực hiện:"]
        for step in doc["steps"]:
            step_desc = f"- Bước {step.get('step', '')}: {step.get('name', '')}. Mô tả: {step.get('description', '')}."
            if step.get("note"):
                step_desc += f" Lưu ý: {step['note']}."
            tech_steps.append(step_desc)
        parts.append("\n".join(tech_steps))
    if doc.get("notes"):
        parts.append(f"Ghi chú chung: {doc['notes']}.")
    return "\n".join(parts)


FORMATTERS = {
    "plant": format_plant_document_to_text,
    "disease_stage": format_disease_stage_document_to_text,
    "cultivation_technique": format_cultivation_technique_document_to_text,
}

def load_text_from_pdf(file_path: str) -> str:
    text = ""
    try:
        reader = pypdf.PdfReader(file_path)
        for page in reader.pages:
            text += page.extract_text() or ""
    except Exception as e:
        print(f"Lỗi khi đọc file PDF {file_path}: {e}")
    return text

def load_text_from_docx(file_path: str) -> str:
    text = ""
    try:
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"Lỗi khi đọc file DOCX {file_path}: {e}")
    return text

def load_text_from_txt(file_path: str) -> str:
    text = ""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    except Exception as e:
        print(f"Lỗi khi đọc file TXT {file_path}: {e}")
    return text


# --- 5. QUÁ TRÌNH INDEXING CHÍNH ---
def index_data():
    print("Bắt đầu quá trình indexing từ nhiều collection...")
    all_chunks = []
    point_id_counter = 0

    for doc_type, mongo_collection_name in COLLECTION_CONFIG.items():
        collection = db[mongo_collection_name]
        formatter = FORMATTERS.get(doc_type)
        if not formatter:
            print(
                f"Cảnh báo: Bỏ qua collection '{mongo_collection_name}' do thiếu hàm format."
            )
            continue
        documents = list(collection.find({}))
        print(
            f"Đang xử lý {len(documents)} tài liệu từ collection '{mongo_collection_name}'..."
        )
        for doc in documents:
            formatted_text = formatter(doc, db)
            if not formatted_text:
                continue
            source_info = json.dumps(
                doc.get("sources", []), default=str, ensure_ascii=False
            )
            chunks = text_splitter.split_text(formatted_text)
            for chunk_text in chunks:
                all_chunks.append(
                    {
                        "text": chunk_text,
                        "metadata": {
                            "source": source_info,
                            "original_doc_id": str(doc.get("_id")),
                            "doc_type": doc_type,
                        },
                    }
                )
    print("--- Hoàn tất xử lý dữ liệu từ MongoDB ---")
    
    # =================================================================
    # === BẮT ĐẦU: PHẦN CODE MỚI - INDEX TỪ FILES ===
    # =================================================================
    print("\n--- Đang xử lý dữ liệu từ các file tài liệu ---")
    documents_dir = "documents" # Tên thư mục chứa file
    if not os.path.exists(documents_dir):
        print(f"Thư mục '{documents_dir}' không tồn tại. Bỏ qua việc index file.")
    else:
        for filename in os.listdir(documents_dir):
            file_path = os.path.join(documents_dir, filename)
            file_content = ""
            if filename.endswith(".pdf"):
                file_content = load_text_from_pdf(file_path)
            elif filename.endswith(".docx"):
                file_content = load_text_from_docx(file_path)
            elif filename.endswith(".txt"):
                file_content = load_text_from_txt(file_path)
            
            if file_content:
                print(f"Đang xử lý file: {filename}")
                # Tạo thông tin nguồn theo cấu trúc bạn đã có
                source_info = json.dumps(
                    [{"name": filename, "url": "local_file"}],
                    default=str,
                    ensure_ascii=False,
                )
                
                chunks = text_splitter.split_text(file_content)
                for chunk_text in chunks:
                    all_chunks.append({
                        "text": chunk_text,
                        "metadata": {
                            "source": source_info,
                            "original_doc_id": filename, # Dùng tên file làm ID
                            "doc_type": "document_file",  # Một loại mới
                        },
                    })
    print("--- Hoàn tất xử lý dữ liệu từ file ---")

    print(f"Tổng cộng đã chia thành {len(all_chunks)} chunks từ tất cả các sources.")

    batch_size = 128
    total_chunks = len(all_chunks)

    for i in range(0, total_chunks, batch_size):
        batch = all_chunks[i : i + batch_size]
        texts_to_embed = ["passage: " + item["text"] for item in batch]

        print(
            f"Đang encoding batch {i//batch_size + 1}/{ (total_chunks + batch_size - 1)//batch_size }..."
        )
        vectors = embedding_model.encode(
            texts_to_embed, show_progress_bar=True
        ).tolist()

        points_to_upsert = []
        for j, item in enumerate(batch):
            points_to_upsert.append(
                models.PointStruct(
                    id=point_id_counter,
                    vector=vectors[j],
                    payload={
                        "content": item["text"],
                        "source": item["metadata"]["source"],
                        "doc_id": item["metadata"]["original_doc_id"],
                        "doc_type": item["metadata"]["doc_type"],
                    },
                )
            )
            point_id_counter += 1

        qdrant_client.upsert(
            collection_name=collection_name, points=points_to_upsert, wait=True
        )
        print(f"Đã index batch {i//batch_size + 1}.")

    print("Hoàn tất quá trình indexing!")


if __name__ == "__main__":
    try:
        qdrant_client.delete_collection(collection_name=collection_name)
        print(f"Đã xóa collection '{collection_name}' cũ.")
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=VECTOR_DIMENSION, distance=models.Distance.COSINE
            ),
        )
        print(f"Đã tạo lại collection '{collection_name}'.")
    except Exception as e:
        print(f"Lỗi khi xóa/tạo lại collection: {e}")
    index_data()
