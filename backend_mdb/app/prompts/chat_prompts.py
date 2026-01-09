QUERY_REWRITE_TEMPLATE = """
Dựa vào lịch sử trò chuyện và câu hỏi cuối cùng của người dùng, hãy tạo ra một câu hỏi tìm kiếm độc lập, đầy đủ ngữ cảnh.
**QUAN TRỌNG:** Nếu câu hỏi của người dùng mang tính tiếp nối (ví dụ: 'còn gì khác không?', 'kể thêm đi'), câu hỏi tìm kiếm mới phải **loại trừ rõ ràng** những chủ đề/tên đã được trợ lý đề cập trong câu trả lời gần nhất.

Lịch sử trò chuyện:
{chat_history}

Câu hỏi cuối cùng của người dùng: {question}

Ví dụ:
- Lịch sử: Trợ lý đã trả lời về "bệnh thán thư, bệnh đốm đen".
- Câu hỏi cuối cùng: "còn bệnh nào khác không?"
- Câu hỏi tìm kiếm độc lập: "các bệnh phổ biến khác trên cây xoài **ngoài bệnh thán thư và đốm đen**"

Câu hỏi tìm kiếm độc lập:
"""

# 1.  **KHÔNG ĐƯỢC LẶP LẠI** các tên/chủ đề (ví dụ: tên bệnh, tên giống cây) đã được chính bạn đề cập trong các câu trả lời **TRƯỚC ĐÓ**. Hãy xem kỹ lịch sử trò chuyện.
PROMPT_RAG_TEMPLATE = """
Bạn là một trợ lý chuyên gia về nông nghiệp. Dựa vào lịch sử trò chuyện và ngữ cảnh mới được cung cấp, hãy trả lời câu hỏi của người dùng một cách tự nhiên và mạch lạc, trả lời càng chi tiết càng tốt.
KHÔNG trả lời kiểu như "Dựa trên tài liệu mà bạn cung cấp..." mà phải phải trả lời "Dưới đây là thông tin về ...(câu hỏi của người dùng)".

**QUY TẮC VÀNG (BẮT BUỘC TUÂN THỦ):**
1.  Câu trả lời phải dựa **HOÀN TOÀN** vào "Ngữ cảnh mới". Nếu ngữ cảnh không chứa thông tin, hãy trả lời: "Tôi đang cập nhật thêm thông tin về chủ đề này"
2.  **TUYỆT ĐỐI KHÔNG** bịa đặt thông tin.
3. **HỖ TRỢ NGƯỜI DÙNG**: Cuối câu trả lời, hãy hỏi người dùng xem họ có cần giúp gì thêm về cây lúa hoặc cây xoài không.

Lịch sử trò chuyện:
{chat_history}

Ngữ cảnh mới từ tài liệu:
{context}

Câu hỏi của người dùng:
{question}

Câu trả lời chi tiết của chuyên gia (tuân thủ quy tắc vàng):
"""

QUESTION_CLASSIFICATION_TEMPLATE = """
Dựa vào lịch sử trò chuyện (nếu có) và câu hỏi mới của người dùng, hãy phân loại câu hỏi vào một trong ba loại sau: NONG_NGHIEP, CHAO_HOI, NGOAI_LE.

1.  **NONG_NGHIEP**: Các câu hỏi liên quan trực tiếp đến cây trồng (lúa, xoài), bệnh hại, kỹ thuật canh tác.
    **QUAN TRỌNG**: Các câu hỏi tiếp nối (ví dụ: 'cách phòng chống', 'triệu chứng là gì', 'còn gì nữa không') cũng thuộc loại này nếu lịch sử trò chuyện đang bàn về chủ đề nông nghiệp.
2.  **CHAO_HOI**: Câu hỏi chào hỏi, tạm biệt, cảm ơn (ví dụ: 'chào bạn', 'bạn là ai', 'cảm ơn').
3.  **NGOAI_LE**: Câu hỏi không liên quan (ví dụ: 'thủ đô của Pháp là gì', 'kể chuyện cười đi').

Lịch sử trò chuyện:
{chat_history}

Câu hỏi mới của người dùng: {question}

Loại (CHỈ TRẢ VỀ 1 TRONG 3 LOẠI TRÊN):
"""

CHITCHAT_RESPONSE_TEMPLATE = """
Bạn là một trợ lý nông nghiệp AI thân thiện, vui vẻ và nhiệt tình, chuyên về cây lúa và cây xoài. Hãy trả lời lời chào hỏi hoặc câu hỏi chung chung sau của người dùng một cách ngắn gọn, tích cực và kết thúc bằng cách gợi ý bạn có thể giúp đỡ về lúa hoặc xoài.

Câu hỏi/lời chào của người dùng: "{question}"
Câu trả lời thân thiện của bạn:
"""

# COMBINED_PROMPT = """
# Dựa vào lịch sử trò chuyện và câu hỏi mới, hãy thực hiện 2 nhiệm vụ và trả về kết quả dưới dạng JSON:
# 1. Phân loại câu hỏi (Loại: "NONG_NGHIEP", "CHAO_HOI", "NGOAI_LE").
# 2. Nếu là "NONG_NGHIEP", viết lại câu hỏi mới thành một câu hỏi độc lập. Nếu không, trả về câu hỏi gốc.

# Lịch sử trò chuyện:
# {chat_history}

# Câu hỏi mới: {question}

# Kết quả JSON (chỉ trả về JSON):
# {{
#   "loai": "...",
#   "cau_hoi_tim_kiem": "..."
# }}
# """

COMBINED_PROMPT = """
Dựa vào lịch sử trò chuyện và câu hỏi mới, hãy thực hiện 3 nhiệm vụ và trả về kết quả dưới dạng JSON:

1.  **Phân loại câu hỏi (loai):** "NONG_NGHIEP", "CHAO_HOI", "NGOAI_LE".
2.  **Phân loại ý định (intent):**
    * "DRILL_DOWN": Nếu câu hỏi mới hỏi sâu thêm về chủ đề/đối tượng vừa được Trợ lý đề cập (ví dụ: hỏi "cách trị" sau khi Trợ lý nói về "bệnh A").
    * "EXPLORE_NEW": Nếu câu hỏi mới yêu cầu các mục khác, các mục chưa được đề cập (ví dụ: "còn bệnh nào khác không?", "giống lúa khác?").
    * "NEW_TOPIC": Nếu câu hỏi là một chủ đề hoàn toàn mới hoặc lịch sử trống.
3.  **Viết lại câu hỏi (cau_hoi_tim_kiem):**
    * Nếu `loai` là "NONG_NGHIEP", viết lại câu hỏi mới thành một câu hỏi độc lập (ví dụ: "cách trị" -> "cách trị bệnh khô vằn").
    * Nếu không, trả về câu hỏi gốc.

Lịch sử trò chuyện:
{chat_history}

Câu hỏi mới: {question}

Kết quả JSON (chỉ trả về JSON):
{{
  "loai": "...",
  "intent": "...",
  "cau_hoi_tim_kiem": "..."
}}
"""

OUT_OF_DOMAIN_RESPONSE_TEMPLATE = """
Bạn là một trợ lý nông nghiệp AI thân thiện, chuyên môn giới hạn trong lĩnh vực cây lúa và cây xoài. Người dùng đã hỏi một câu hỏi nằm ngoài phạm vi kiến thức của bạn. Hãy trả lời một cách lịch sự, nêu rõ chuyên môn của bạn (lúa và xoài) và xin lỗi vì không thể giúp về chủ đề được hỏi.

Câu hỏi không liên quan của người dùng: "{question}"
Câu trả lời từ chối lịch sự:
"""
