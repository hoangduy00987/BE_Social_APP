
import re
from ..llm.llm_client import client
import json

def extract_entities(sentence):
    prompt = f"""
Hãy trích xuất TẤT CẢ các thực thể (entities) quan trọng trong câu sau,
bao gồm:
- Con người (PERSON)
- Quốc gia, tỉnh thành, khu vực, địa điểm (LOCATION)
- Tổ chức, cơ quan, doanh nghiệp, câu lạc bộ (ORGANIZATION)
- Sự kiện (EVENT): trận đấu, hội nghị, tai nạn, thiên tai, giải đấu...
- Sản phẩm / vật thể (OBJECT)
- Chính sách, luật, quyết định (LAW / POLICY)
- Thời gian (TIME)

KHÔNG xem số liệu, tỉ số, số tiền, phần trăm… là entity.
Ví dụ: 2-0, 30%, 200 triệu, 1.2 tỷ → KHÔNG phải entity.

Quy tắc trích xuất:
- Giữ nguyên văn bản entity như trong câu.
- Gộp entities nhiều từ thành một thực thể duy nhất.
- Trả về JSON LIST, ví dụ:
  ["Việt Nam", "Lào", "vòng loại Asian Cup 2027"]

Câu:
"{sentence}"
"""


    print("\n==============================")
    print("=== LLM ENTITY EXTRACTION ===")
    print("==============================")
    print("Input sentence:", sentence)
    print("------------------------------")

    completion = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    resp = completion.choices[0].message.content

    print("\n=== RAW LLM OUTPUT ===")
    print(resp)
    print("------------------------------")

    cleaned = re.sub(r"```json|```", "", resp).strip()

    try:
        entities = json.loads(cleaned)
    except Exception as e:
        print("⚠ ERROR PARSING JSON:", e)
        print("Returned text:", cleaned)
        return []

    print("\n=== PARSED ENTITIES ===")
    for e in entities:
        print(" -", e)
    print("==============================\n")

    return entities
