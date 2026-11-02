import argparse, json, math, os, re
from pathlib import Path
import requests

ROOT = Path(__file__).parent
EMBED_MODEL = "bge-m3"
OLLAMA = "http://127.0.0.1:11434"

def cat_doan(text: str) -> list[str]:
    cleaned = text.lstrip("\ufeff").replace("\r\n", "\n")
    chunks = [p.strip() for p in re.split(r"(?=^## Điều \d+\.)", cleaned, flags=re.MULTILINE) if re.match(r"^## Điều \d+\.", p.strip())]
    if not chunks:
        raise ValueError("Không tìm thấy điều khoản nào")
    seen = set()
    for c in chunks:
        num = int(re.match(r"^## Điều (\d+)\.", c).group(1))
        if num in seen:
            raise ValueError(f"Trùng lặp: Điều {num}")
        seen.add(num)
    return chunks

def nhung(input_path: Path = ROOT / "quy_che.md", output_path: Path = ROOT / "chi_muc.json") -> list[dict]:
    chunks = cat_doan(Path(input_path).read_text(encoding="utf-8"))
    resp = requests.post(f"{OLLAMA}/api/embed", json={"model": EMBED_MODEL, "input": chunks}, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    if not isinstance(data, dict):
        raise ValueError("Phản hồi không phải dict")
    vecs = data.get("embeddings") or data.get("vectors")
    if not isinstance(vecs, list) or len(vecs) != len(chunks):
        raise ValueError("Số vector không khớp số đoạn")
    dim = len(vecs[0]) if vecs and isinstance(vecs[0], list) and len(vecs[0]) > 0 else 0
    if dim == 0:
        raise ValueError("Chiều vector không hợp lệ")
    for v in vecs:
        if not isinstance(v, list) or len(v) != dim or not all(isinstance(x, (int, float)) and math.isfinite(x) for x in v) or all(x == 0.0 for x in v):
            raise ValueError("Vector không hợp lệ hoặc bằng 0")
    rows = [{"nguon": c.splitlines()[0].lstrip("#").strip(), "noi_dung": c, "vec": [float(x) for x in v]} for c, v in zip(chunks, vecs)]
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(f"{out.suffix}.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    os.replace(tmp, out)
    return rows

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--input", default=ROOT / "quy_che.md", type=Path)
    p.add_argument("--output", default=ROOT / "chi_muc.json", type=Path)
    args = p.parse_args()
    res = nhung(input_path=args.input, output_path=args.output)
    print(f"Đã nhúng {len(res)} đoạn, chiều vector: {len(res[0]['vec']) if res else 0}")
