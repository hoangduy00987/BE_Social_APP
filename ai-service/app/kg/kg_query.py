from app.kg.neo4j_client import get_session

from app.kg.neo4j_client import get_session
import re

def query_kg_for_entities(entities):
    triples = []
    if len(entities) < 2:
        return triples

    # Tạo tất cả cặp entity
    pairs = []
    for i in range(len(entities)):
        for j in range(i + 1, len(entities)):
            pairs.append((entities[i], entities[j]))

    query = """
    WITH split(toLower($ent2), " ") AS tokens
    MATCH (a:Entity)-[r]-(b:Entity)
    WHERE 
    (
        toLower(a.name) CONTAINS toLower($ent1)
        AND toLower(b.name) CONTAINS toLower($ent2)
    )
    OR
    (
        toLower(a.name) CONTAINS toLower($ent2)
        AND toLower(b.name) CONTAINS toLower($ent1)
    )
    OR 
    (
        toLower(r.example) CONTAINS toLower($ent1)
        AND ALL(t IN tokens WHERE toLower(r.example) CONTAINS t)
    )
    WITH a, b, r
    OPTIONAL MATCH (art:Article)-[:MENTIONS]->(a)
    OPTIONAL MATCH (art)-[:HAS_CATEGORY]->(cat:Category)
    RETURN DISTINCT
        a.name AS source,
        type(r) AS relation,
        b.name AS target,
        r.example AS evidence,
        cat.name AS category,
        properties(r) AS props;
        """

    with get_session() as session:
        for ent1, ent2 in pairs:
            records = session.run(query, ent1=ent1, ent2=ent2)

            for r in records:
                row = dict(r)

                # ------------------------------
                # LỌC NOISE Ở MỨC 1 – Evidence phải tồn tại
                # ------------------------------
                ev = (row.get("evidence") or "").lower()
                if ev.strip() == "":
                    continue

                # ------------------------------
                # LỌC NOISE Ở MỨC 2 – Evidence phải CHỨA ent1 hoặc ent2
                # ------------------------------
                if not (
                    ent1.lower() in ev or ent2.lower() in ev
                ):
                    # bỏ những bài không liên quan (ma túy, chính trị...)
                    continue

                # ------------------------------
                # LỌC NOISE Ở MỨC 3 – Không cho entity lỗi như "tuyển Việt Namrơi"
                # ------------------------------
                if re.search(r"[a-zA-Z0-9]+rơi", row["source"].lower()):
                    continue
                if re.search(r"[a-zA-Z0-9]+rơi", row["target"].lower()):
                    continue

                triples.append(row)

    return triples


# WITH split(toLower($ent2), " ") AS tokens
#     MATCH (a:Entity)-[r]-(b:Entity)
#     WHERE 
#     (
#         toLower(a.name) CONTAINS toLower($ent1)
#     AND toLower(b.name) CONTAINS toLower($ent2)
#     )
#     OR
#     (
#         toLower(a.name) CONTAINS toLower($ent2)
#     AND toLower(b.name) CONTAINS toLower($ent1)
#     )
#     OR
#     (
#         toLower(r.example) CONTAINS toLower($ent1)
#     AND ALL(t IN tokens WHERE toLower(r.example) CONTAINS t)
#     )
#     RETURN DISTINCT
#         a.name AS source,
#         type(r) AS relation,
#         b.name AS target,
#         r.example AS evidence,
#         properties(r) AS props;