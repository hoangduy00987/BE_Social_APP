from underthesea import ner
import re
from ..llm.llm_client import client
import json
# def extract_entities(sentence: str):
#     result = ner(sentence)
#     print("\n=== NER OUTPUT ===")
#     print(result)

#     entities = []
#     current = []

#     print("\n=== PROCESSING ===")

#     for word, pos, chunk, tag in result:
#         print(f"Word: {word:15}  Tag: {tag}")

#         # CASE 1: Start BIO entity
#         if tag.startswith("B-"):
#             if current:
#                 entities.append(" ".join(current))
#             current = [word]

#         # CASE 2: Continue BIO entity
#         elif tag.startswith("I-"):
#             current.append(word)

#         else:
#             # CASE 3: Tag O but contains proper noun inside token 
#             # Example: "Lào 2-0"
#             subwords = re.findall(r"\b[A-Z][a-zA-ZÀ-ỹ]+", word)
#             for sw in subwords:
#                 print(f" --> DETECT SUB-ENTITY: {sw}")
#                 entities.append(sw)

#             # finish BIO entity if exists
#             if current:
#                 entities.append(" ".join(current))
#                 current = []

#     # finalize last BIO entity
#     if current:
#         entities.append(" ".join(current))

#     # Lọc entity
#     final_entities = list(set(e for e in entities if len(e.strip()) > 1))

#     print("\n=== FINAL ENTITIES ===")
#     print(final_entities)

#     return final_entities
# def llm_extract_entities(sentence):
#     prompt = f"""
#     Hãy trích xuất TẤT CẢ các thực thể (entities) quan trọng trong câu sau,
#     bao gồm nhưng không giới hạn:
#     - Con người (PERSON)
#     - Quốc gia, tỉnh thành, khu vực, địa điểm (LOCATION)
#     - Tổ chức, cơ quan, doanh nghiệp, câu lạc bộ (ORGANIZATION)
#     - Sự kiện (EVENT): trận đấu, hội nghị, tai nạn, thiên tai, giải đấu...
#     - Sản phẩm / vật thể (PRODUCT / OBJECT)
#     - Chính sách, luật, quyết định (LAW / POLICY)
#     - Số liệu, tỉ lệ, thống kê (QUANTITY)
#     - Thời gian (TIME)

#     Quy tắc trích xuất:
#     - Giữ nguyên văn bản entity như trong câu.
#     - Không tạo thêm hoặc suy luận entity không xuất hiện.
#     - Gộp entities nhiều từ (multi-word entity) thành một thực thể duy nhất.
#     - Chỉ trả về JSON LIST duy nhất, ví dụ:
#       ["Việt Nam", "Lào", "vòng loại Asian Cup 2027"]

#     Câu cần xử lý:
#     "{sentence}"
#     """

#     completion = client.chat.completions.create(
#         model="gpt-4.1-mini",
#         messages=[{"role": "user", "content": prompt}]
#     )

#     resp = completion.choices[0].message.content
#     cleaned = re.sub(r"```json|```", "", resp).strip()
#     return json.loads(cleaned)

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
