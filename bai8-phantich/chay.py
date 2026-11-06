import argparse, sqlite3
from pathlib import Path

DEFAULT_DB = str(Path(__file__).resolve().parent / "phan_tich.db")

def split_statements(sql_text):
    stmts, cur = [], ""
    for ch in sql_text:
        cur += ch
        if ch == ";" and sqlite3.complete_statement(cur):
            stmts.append(cur.strip()); cur = ""
    if cur.strip(): stmts.append(cur.strip())
    return stmts

def query_ro(database, sql_text):
    p = Path(database).resolve()
    if not p.exists(): raise FileNotFoundError(f"Database not found: {database}")
    conn = sqlite3.connect(p.as_uri() + "?mode=ro", uri=True)
    try:
        results = []
        for stmt in split_statements(sql_text):
            cur = conn.execute(stmt)
            if cur.description:
                results.append(([d[0] for d in cur.description], cur.fetchall()))
        return results
    finally: conn.close()

def chay(sql_path, database=None, init=False):
    db, sql_text = database or DEFAULT_DB, Path(sql_path).read_text(encoding="utf-8")
    if init:
        p = Path(db).resolve()
        p.parent.mkdir(parents=True, exist_ok=True); open(p, "xb").close()
        conn = sqlite3.connect(str(p))
        try: conn.executescript(sql_text)
        finally: conn.close()
        return []
    results = query_ro(db, sql_text)
    for cols, rows in results:
        print(" | ".join(cols))
        for row in rows: print(" | ".join(str(v) for v in row))
    return results

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("sql"); p.add_argument("--database", default=DEFAULT_DB); p.add_argument("--init", action="store_true")
    a = p.parse_args()
    chay(a.sql, a.database, a.init)
