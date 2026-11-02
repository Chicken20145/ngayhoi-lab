import argparse, json, re
from pathlib import Path

try:
    from tim import tim
except ImportError:
    from .tim import tim

ROOT = Path(__file__).parent

def _extract_dieu_num(text: str) -> str:
    m = re.search(r"Điều\s*(\d+)", text)
    return m.group(1) if m else ""

def danh_gia(question_path: Path = ROOT / "cau_hoi_vang.json", index_path: Path = ROOT / "chi_muc.json") -> dict:
    with open(Path(question_path), "r", encoding="utf-8") as f:
        questions = json.load(f)
    dung = 0
    chi_tiet = []
    for item in questions:
        hoi = item.get("hoi", "")
        target = item.get("dieu", "")
        t_num = _extract_dieu_num(target)
        top3 = tim(hoi, k=3, index_path=index_path)
        top_src = [d[1].get("nguon", "") for d in top3]
        hit = any(_extract_dieu_num(s) == t_num for s in top_src if t_num)
        if hit:
            dung += 1
        chi_tiet.append({"hoi": hoi, "dieu": target, "top3": top_src, "dung": hit})
    tong = len(questions)
    return {"dung": dung, "tong": tong, "recall_at_3": (dung / tong if tong > 0 else 0.0), "chi_tiet": chi_tiet}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--questions", default=ROOT / "cau_hoi_vang.json", type=Path)
    p.add_argument("--index", default=ROOT / "chi_muc.json", type=Path)
    args = p.parse_args()
    res = danh_gia(question_path=args.questions, index_path=args.index)
    for i, c in enumerate(res["chi_tiet"], 1):
        print(f"{i}. [{'ĐÚNG' if c['dung'] else 'SAI'}] {c['hoi']} -> {c['dieu']} | {', '.join(c['top3'])}")
    print(f"Recall@3: {res['dung']}/{res['tong']} ({res['recall_at_3']:.2%})")
