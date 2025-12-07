from app.kg.entity_extractor import extract_entities
from app.kg.kg_query import query_kg_for_entities

from app.llm.split_claims import split_claims
from app.kg.entity_extractor import extract_entities
from app.kg.kg_query import query_kg_for_entities
from app.llm.reasoning import llm_reasoning,llm_filter_evidence,detect_claim_category


def verify_claim(claim: str):
    claims = split_claims(claim)
    results = []

    for c in claims:
        entities = extract_entities(c)
        new_claim = detect_claim_category(c)
        # triples = query_kg_for_entities(entities)
        triples = llm_filter_evidence(c, query_kg_for_entities(entities),new_claim)

        if not triples:
            results.append({
                "claim": c,
                "verdict": "NEI",
                "explanation": "Không tìm thấy thông tin gì của sự kiện trên."
            })
            continue

        evidence_text = "\n".join([
            f"- {t['source']} ({t['relation']}) {t['target']} : {t.get('evidence','')}"
            for t in triples
        ])


        result = llm_reasoning(c, evidence_text)
        result["claim"] = c
        results.append(result)

    return results
