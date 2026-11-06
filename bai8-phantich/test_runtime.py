import csv, sqlite3, sys, tempfile, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from nap import nap
from chay import query_ro, chay

class TestRuntime(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = self.tmp.name
    def tearDown(self): self.tmp.cleanup()

    def _write_csvs(self, dk_h, dk_r, dd_h, dd_r):
        with open(Path(self.d) / "dang_ky.csv", "w", newline="", encoding="utf-8-sig") as f:
            csv.writer(f).writerow(dk_h); csv.writer(f).writerows(dk_r)
        with open(Path(self.d) / "diem_danh.csv", "w", newline="", encoding="utf-8-sig") as f:
            csv.writer(f).writerow(dd_h); csv.writer(f).writerows(dd_r)

    def test_nap_retains_text_and_counts(self):
        self._write_csvs(["ma_sv", "ma_phien"], [[" sv01 ", "p01"]],
                         ["ma_sv", "ma_phien", "phut_tre"], [[" sv01 ", "p01", "  "]])
        db = str(Path(self.d) / "out.db")
        self.assertEqual(nap(self.d, db), {"dang_ky": 1, "diem_danh": 1})
        conn = sqlite3.connect(db)
        try:
            self.assertEqual(conn.execute("SELECT * FROM dang_ky").fetchall(), [(" sv01 ", "p01")])
            self.assertEqual(conn.execute("SELECT * FROM diem_danh").fetchall(), [(" sv01 ", "p01", "  ")])
        finally: conn.close()

    def test_nap_rejects_invalid_header_without_creating_db(self):
        self._write_csvs(["bad", "ma_phien"], [["1", "2"]],
                         ["ma_sv", "ma_phien", "phut_tre"], [["1", "2", "3"]])
        db = Path(self.d) / "no.db"
        with self.assertRaises(ValueError): nap(self.d, str(db))
        self.assertFalse(db.exists())

    def test_nap_refuses_existing_db(self):
        self._write_csvs(["ma_sv", "ma_phien"], [["1", "2"]],
                         ["ma_sv", "ma_phien", "phut_tre"], [["1", "2", "3"]])
        db = Path(self.d) / "exist.db"
        db.write_bytes(b"ORIGINAL_BYTES")
        with self.assertRaises(FileExistsError): nap(self.d, str(db))
        self.assertEqual(db.read_bytes(), b"ORIGINAL_BYTES")

    def test_sql_read_ro_and_rejects_writes(self):
        no_db = str(Path(self.d) / "nonexistent.db")
        with self.assertRaises(FileNotFoundError): query_ro(no_db, "SELECT 1;")
        self.assertFalse(Path(no_db).exists())
        db = str(Path(self.d) / "ro.db")
        conn = sqlite3.connect(db)
        try: conn.executescript("CREATE TABLE t (x TEXT); INSERT INTO t VALUES ('ok');")
        finally: conn.close()
        self.assertEqual(query_ro(db, "SELECT * FROM t;"), [(["x"], [("ok",)])])
        with self.assertRaises(sqlite3.OperationalError): query_ro(db, "INSERT INTO t VALUES ('fail');")

    def test_chay_init_and_query_split(self):
        db = str(Path(self.d) / "init.db")
        init_sql, query_sql = Path(self.d) / "init.sql", Path(self.d) / "query.sql"
        init_sql.write_text("CREATE TABLE a (v TEXT); INSERT INTO a VALUES ('val');", encoding="utf-8")
        chay(str(init_sql), database=db, init=True)
        with self.assertRaises(FileExistsError): chay(str(init_sql), database=db, init=True)
        query_sql.write_text("SELECT 'a;b' AS c1; SELECT * FROM a;", encoding="utf-8")
        res = chay(str(query_sql), database=db, init=False)
        self.assertEqual(res, [(["c1"], [("a;b",)]), (["v"], [("val",)])])

if __name__ == "__main__":
    unittest.main()
