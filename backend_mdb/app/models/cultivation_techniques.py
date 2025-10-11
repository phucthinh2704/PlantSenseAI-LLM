from pydantic import BaseModel, Field
from typing import Optional, List
from .source import Source
from datetime import datetime

class TechniqueStep(BaseModel):
    step: int
    name: str
    description: str
    note: Optional[str] = None


class CultivationTechnique(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    name: str  # Tên kỹ thuật canh tác
    plant_ids: List[str]  # Liên kết cây trồng/giống

    # === Mô tả chi tiết ===
    description: Optional[str] = Field(
        default=None, description="Mô tả tổng quan kỹ thuật, mục đích và ý nghĩa"
    )
    requirements: Optional[str] = Field(
        default=None, description="Điều kiện áp dụng: đất, khí hậu, giống, phân bón..."
    )
    benefits: Optional[str] = Field(
        default=None,
        description="Lợi ích đạt được: tăng năng suất, giảm chi phí, chống sâu bệnh...",
    )

    # === Phân loại & ứng dụng (quan trọng cho phân tích luận văn) ===
    category: str = Field(
        ..., description="Phân loại kỹ thuật (VD: 'Bón phân', 'Tưới tiêu', 'Làm đất')"
    )
    application_period: str = Field(
        ...,
        description="Giai đoạn áp dụng (VD: 'Giai đoạn cây con', 'Trước trỗ', 'Sau thu hoạch')",
    )

    # === Quy trình chi tiết ===
    steps: List[TechniqueStep] = Field(
        default_factory=list, description="Các bước thực hiện cụ thể"
    )

    image_url: Optional[str] = Field(default=None, description="URL hình minh họa")
    notes: Optional[str] = Field(default=None, description="Ghi chú thêm")
    
    # === Thêm trường để phân biệt giữa lúa và xoài ===
    crop_type: str = Field(..., description="Loại cây trồng (VD: 'Lúa', 'Xoài')")
    
    sources: List[Source] = Field(
        default_factory=list, 
        description="Danh sách các nguồn tham khảo cho kỹ thuật này"
    )

    # === Metadata ===
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
