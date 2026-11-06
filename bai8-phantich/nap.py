import argparse, csv, sqlite3
from pathlib import Path

def nap(data_dir, database):
    with open(Path(data_dir) / "dang_ky.csv", "r", encoding="utf-8-sig", newline="") as f:
        r = csv.reader(f)
        if next(r, None) != ["ma_sv", "ma_phien"]: raise ValueError("Header error")
        dk_rows = list(r)
        if any(len(row) != 2 for row in dk_rows): raise ValueError("Row shape error")
    with open(Path(data_dir) / "diem_danh.csv", "r", encoding="utf-8-sig", newline="") as f:
        r = csv.reader(f)
        if next(r, None) != ["ma_sv", "ma_phien", "phut_tre"]: raise ValueError("Header error")
        dd_rows = list(r)
        if any(len(row) != 3 for row in dd_rows): raise ValueError("Row shape error")
    p = Path(database).resolve()
    p.parent.mkdir(parents=True, exist_ok=True); open(p, "xb").close()
    conn = sqlite3.connect(str(p))
    try:
        conn.executescript("CREATE TABLE dang_ky (ma_sv TEXT, ma_phien TEXT); CREATE TABLE diem_danh (ma_sv TEXT, ma_phien TEXT, phut_tre TEXT);")
        conn.executemany("INSERT INTO dang_ky (ma_sv, ma_phien) VALUES (?, ?);", dk_rows)
        conn.executemany("INSERT INTO diem_danh (ma_sv, ma_phien, phut_tre) VALUES (?, ?, ?);", dd_rows)
        conn.commit()
    finally: conn.close()
    counts = {"dang_ky": len(dk_rows), "diem_danh": len(dd_rows)}
    print(f"dang_ky: {counts['dang_ky']}, diem_danh: {counts['diem_danh']}")
    return counts

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--data", required=True); p.add_argument("--database", required=True)
    a = p.parse_args()
    nap(a.data, a.database)
