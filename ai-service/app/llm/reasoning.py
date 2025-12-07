import json
import re
from .llm_client import client  # client = OpenAI(api_key=...)
import os
import json
import pandas as pd

def detect_claim_category(claim: str) -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "category.csv")

    print("📌 Đang load Category CSV từ:", csv_path)

    # Check tồn tại file
    if not os.path.exists(csv_path):
        print("❌ Không tìm thấy category.csv")
        return None
    # Load CSV
    df = pd.read_csv(csv_path)
    categories = df['category'].dropna().str.strip().unique().tolist()

    categories_text = ", ".join(categories)

    prompt = f"""
    Bạn là hệ thống phân loại tin tức theo lĩnh vực.

    Claim: "{claim}"

    Các lĩnh vực hiện có:
    {categories_text}

    Chỉ trả về duy nhất tên lĩnh vực phù hợp nhất.
    """

    completion = client.chat.completions.create(
        model="GPT‑4o mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return completion.choices[0].message.content.strip()


def llm_filter_evidence(claim, triples, claim_category):
    print("\n=== FILTER BY CATEGORY STEP ===")
    print("Category detected for claim:", claim_category)

    # 1️⃣ Lọc triples theo category phù hợp trước khi gọi LLM
    category_filtered = []
    for t in triples:
        cat = t.get("category", "")
        if claim_category in cat:
            category_filtered.append(t)

    print("\nTriples after category filtering:")
    print(json.dumps(category_filtered, indent=2, ensure_ascii=False))

    # Nếu lọc hết → fallback giữ tất cả triples
    if not category_filtered:
        print("\n⚠ No category matched — fallback to all triples")
        category_filtered = triples

    # 2️⃣ Chỉ gửi evidence text sang LLM
    evidence_sentences = [
        t.get("evidence", "") for t in category_filtered if t.get("evidence")
    ]

    print("\nEvidence sent to LLM:")
    print(json.dumps(evidence_sentences, indent=2, ensure_ascii=False))

    # Prompt lọc theo nội dung
    prompt = f"""
    Claim:
    "{claim}"

    Dưới đây là các câu evidence đã qua bước lọc theo category:
    {json.dumps(evidence_sentences, ensure_ascii=False)}

    Nhiệm vụ:
    - Chỉ giữ lại những câu liên quan trực tiếp để kiểm chứng claim
    - Trả về JSON LIST duy nhất gồm các câu evidence phù hợp
    """

    completion = client.chat.completions.create(
        model="GPT‑4o mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    resp = completion.choices[0].message.content.strip()
    cleaned = re.sub(r"```json|```", "", resp).strip()

    try:
        selected_sentences = json.loads(cleaned)
    except:
        print("\n⚠ Parse failed — fallback to category-filtered triples")
        return category_filtered

    # Map sentence → triple
    final = []
    for s in selected_sentences:
        for t in category_filtered:
            if s == t.get("evidence"):
                final.append(t)
                break

    print("\n=== FINAL TRIPLES SELECTED:")
    print(json.dumps(final, indent=2, ensure_ascii=False))

    return final





def llm_reasoning(claim: str, evidence: str):
    prompt = f"""
    Bạn là trợ lý kiểm chứng thông tin dựa trên tri thức có cấu trúc từ Knowledge Graph.

    Nhiệm vụ của bạn:

    1. Ưu tiên xác định claim là TRUE hoặc FALSE trước.
    - Nếu Knowledge Graph chứa thông tin hỗ trợ claim → trả lời TRUE.
    - Nếu Knowledge Graph có thông tin mâu thuẫn, phủ định claim → trả lời FALSE.

    2. Chỉ trả lời NEI khi thật sự không có bất kỳ dữ kiện nào liên quan đến claim,
    hoặc các dữ kiện không đủ để kết luận rõ ràng.

    3. Giải thích bằng tiếng Việt, tự nhiên và thuyết phục,
    dựa vào hiểu biết từ các facts trong Knowledge Graph,
    nhưng không được trích nguyên văn entity hoặc quan hệ.
    Hãy chuyển chúng thành câu mô tả tự nhiên.

    Dữ liệu:

    CLAIM: "{claim}"

    FACTS TỪ KNOWLEDGE GRAPH:
    {evidence}

    Hãy trả về JSON với cấu trúc:
    {{
        "verdict": "TRUE | FALSE | NEI",
        "explanation": ""Lời giải thích phải tự nhiên như người thật, chỉ tập trung vào nội dung của claim và thông tin đã cho. 
Không nhắc đến 'Knowledge Graph', 'bằng chứng', 'dữ liệu', 'nguồn', 'hệ thống', 
hay bất kỳ yếu tố kỹ thuật nào. 
Chỉ mô tả lại sự kiện một cách mạch lạc, dễ hiểu và logic như đang tường thuật lại nội dung."
"
    }}
    """

    completion = client.chat.completions.create(
    model="GPT‑4o mini",
    messages=[
        {"role": "user", "content": prompt}
    ]
)

    resp_text = completion.choices[0].message.content

    cleaned = re.sub(r"```json|```", "", resp_text).strip()
    return json.loads(cleaned)

