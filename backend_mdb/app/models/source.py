from pydantic import BaseModel, Field
from datetime import date

class Source(BaseModel):
    name: str  # Tên nguồn, VD: "Viện Lúa ĐBSCL", "Báo Nông nghiệp Việt Nam"
    url: str   # URL chính xác của bài viết lấy thông tin
    retrieved_at: date = Field(default_factory=date.today) # Ngày lấy dữ liệu