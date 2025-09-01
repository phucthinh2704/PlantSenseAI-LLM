# main.py hoặc file kết nối database
import os
from dotenv import load_dotenv

# Import thư viện Motor thay vì PyMongo
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING

# Tải biến môi trường
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")

# Kiểm tra xem các biến môi trường có được tải không
if not MONGO_URI or not MONGO_DB:
    raise ValueError("MONGO_URI and MONGO_DB environment variables must be set.")

try:
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[MONGO_DB]
    print("Kết nối thành công với MongoDB!")

except Exception as e:
    print("Không thể kết nối với MongoDB:", e)
    import sys

    sys.exit(1)

# Collection
user_collection = db["users"]

# Tạo index bất đồng bộ
async def create_indexes():
    """Tạo các index cần thiết cho collection."""
    await user_collection.create_index([("email", ASCENDING)], unique=True)
    print("Đã tạo index cho trường 'email'.")

