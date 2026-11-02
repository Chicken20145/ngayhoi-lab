import argparse, json, math
from pathlib import Path
import numpy as np
import requests

ROOT = Path(__file__).parent
EMBED_MODEL = "bge-m3"
OLLAMA = "http://127.0.0.1:11434"

def tim(question: str, k: int = 3, index_path: Path = ROOT / "chi_muc.json") -> list[tuple[float, dict]]:
    if not isinstance(question, str) or not question.strip():
        raise ValueError("Câu hỏi không được rỗng")
    if not isinstance(k, int) or k < 1:
        raise ValueError("k phải là số nguyên >= 1")
    idx_path = Path(index_path)
    if not idx_path.exists():
        raise FileNotFoundError(f"Không tìm thấy: {idx_path}")
    with open(idx_path, "r", encoding="utf-8") as f:
        index = json.load(f)
    if not index:
        raise ValueError("Chỉ mục rỗng")
    row_vecs = [r.get("vec") for r in index]
    if not all(isinstance(v, list) and len(v) > 0 for v in row_vecs):
        raise ValueError("Chỉ mục chứa vector không hợp lệ")
    dim = len(row_vecs[0])
    for v in row_vecs:
        if len(v) != dim or not all(isinstance(x, (int, float)) and math.isfinite(x) for x in v) or all(x == 0.0 for x in v):
            raise ValueError("Vector chỉ mục không hợp lệ hoặc bằng 0")
    resp = requests.post(f"{OLLAMA}/api/embed", json={"model": EMBED_MODEL, "input": [question.strip()]}, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    if not isinstance(data, dict):
        raise ValueError("Phản hồi không phải dict")
    q_vecs = data.get("embeddings") or data.get("vectors")
    if not isinstance(q_vecs, list) or len(q_vecs) != 1:
        raise ValueError("Không nhận được vector câu hỏi")
    q_vec = q_vecs[0]
    if not isinstance(q_vec, list) or len(q_vec) != dim or not all(isinstance(x, (int, float)) and math.isfinite(x) for x in q_vec) or all(x == 0.0 for x in q_vec):
        raise ValueError("Vector câu hỏi không hợp lệ")
    matrix = np.array(row_vecs, dtype=float)
    query = np.array(q_vec, dtype=float)
    q_norm = np.linalg.norm(query)
    m_norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    if q_norm == 0 or not np.isfinite(q_norm) or np.any(m_norms == 0) or not np.all(np.isfinite(m_norms)):
        raise ValueError("Độ dài vector không hợp lệ")
    scores = np.dot(matrix / m_norms, query / q_norm)
    if not np.all(np.isfinite(scores)):
        raise ValueError("Điểm tương đồng chứa NaN")
    order = np.argsort(-scores)[:k]
    return [(float(scores[i]), index[i]) for i in order]

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("question", type=str)
    p.add_argument("--index", default=ROOT / "chi_muc.json", type=Path)
    args = p.parse_args()
    for s, doc in tim(args.question, k=3, index_path=args.index):
        print(f"{s:.4f} | {doc.get('nguon', '')}")
