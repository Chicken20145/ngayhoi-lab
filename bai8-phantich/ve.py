import argparse
from pathlib import Path
try: from chay import query_ro
except ImportError: from .chay import query_ro
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ImportError: plt = None

def ve(database, output):
    if plt is None: raise ImportError("matplotlib is required for plotting")
    sql_path = Path(__file__).resolve().parent / "theo_phien.sql"
    results = query_ro(database, sql_path.read_text(encoding="utf-8"))
    rows = results[0][1] if results else []
    sessions, ns = [str(r[0]) for r in rows], [int(r[1]) for r in rows]
    attendeds, percents = [int(r[2]) for r in rows], [float(r[3]) for r in rows]
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(range(len(sessions)), percents, width=0.6, color="steelblue")
    ax.set_ylim(0, 100); ax.set_ylabel("Tỷ lệ (%)")
    ax.set_xticks(range(len(sessions))); ax.set_xticklabels([f"{s}\n(n={n})" for s, n in zip(sessions, ns)])
    ax.set_title("Tỷ lệ lượt đăng ký có quét mã, theo phiên")
    for bar, att, n, pct in zip(bars, attendeds, ns, percents):
        ax.annotate(f"{att}/{n} ({pct:.1f}%)", (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    ha="center", va="bottom", fontsize=8, xytext=(0, 2), textcoords="offset points")
    fig.text(0.5, 0.02,
             "Nguồn: Dữ liệu mô phỏng khóa học (synthetic course). Định nghĩa: cặp SV-phiên đã đăng ký có ít nhất 1 lần quét, bỏ trùng / số lượt đăng ký; phút trống vẫn tính có đến, không suy ra đúng giờ.",
             ha="center", fontsize=8, color="dimgray", wrap=True)
    fig.subplots_adjust(bottom=0.15)
    p = Path(output).resolve()
    p.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(p), format="png", bbox_inches="tight"); plt.close(fig)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--database", required=True); p.add_argument("--output", required=True)
    a = p.parse_args()
    ve(a.database, a.output)
