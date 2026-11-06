from pathlib import Path
import sqlite3
import unittest

DIR = Path(__file__).parent

def read_sql(name: str) -> str:
    return (DIR / name).read_text(encoding="utf-8")

class TestPhanTich(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.executescript(read_sql("mini.sql"))

    def tearDown(self):
        self.conn.close()

    def test_ty_le_50_percent(self):
        attended, registered, percent = self.conn.execute(read_sql("ty_le.sql")).fetchone()
        self.assertEqual(attended, 2)
        self.assertEqual(registered, 4)
        self.assertAlmostEqual(percent, 50.0, places=2)

    def test_injective_pair_collision(self):
        self.conn.execute("DELETE FROM dang_ky")
        self.conn.execute("DELETE FROM diem_danh")
        self.conn.executemany("INSERT INTO dang_ky VALUES (?, ?)", [("A_B", "C"), ("A", "B_C")])
        self.conn.executemany("INSERT INTO diem_danh VALUES (?, ?, ?)", [("A_B", "C", ""), ("A", "B_C", "")])
        attended, registered, _ = self.conn.execute(read_sql("ty_le.sql")).fetchone()
        self.assertEqual(registered, 2)
        self.assertEqual(attended, 2)

    def test_wrong_baseline_100_percent(self):
        scans, registered, percent = self.conn.execute(read_sql("ty_le_ai.sql")).fetchone()
        self.assertEqual(scans, 4)
        self.assertEqual(registered, 4)
        self.assertAlmostEqual(percent, 100.0, places=2)

    def test_theo_phien(self):
        self.conn.execute("INSERT INTO dang_ky VALUES ('X', 'P02')")
        rows = self.conn.execute(read_sql("theo_phien.sql")).fetchall()
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0], ("P01", 4, 2, 50.0))
        self.assertEqual(rows[1], ("P02", 1, 0, 0.0))

    def test_empty_denominator_safe(self):
        self.conn.execute("DELETE FROM dang_ky")
        attended, registered, percent = self.conn.execute(read_sql("ty_le.sql")).fetchone()
        self.assertEqual(attended, 0)
        self.assertEqual(registered, 0)
        self.assertIsNone(percent)

    def test_blank_minutes_attended(self):
        trong = self.conn.execute(read_sql("trong.sql")).fetchall()
        self.assertTrue(any(r[0] == "A" for r in trong))
        attended, registered, _ = self.conn.execute(read_sql("ty_le.sql")).fetchone()
        self.assertEqual((attended, registered), (2, 4))

    def test_anomalies(self):
        self.assertEqual(self.conn.execute(read_sql("trung.sql")).fetchall(), [("A", "P01", 2)])
        self.assertEqual(self.conn.execute(read_sql("viet_thuong.sql")).fetchall(), [("B", "p01")])
        trong = self.conn.execute(read_sql("trong.sql")).fetchall()
        self.assertEqual(len(trong), 1)
        self.assertEqual(trong[0][0], "A")
        self.assertEqual(self.conn.execute(read_sql("nguoi_la.sql")).fetchall(), [("E", "P01")])

    def test_ho_so(self):
        stmts, buf = [], ""
        for line in read_sql("ho_so.sql").splitlines():
            buf += line + "\n"
            if sqlite3.complete_statement(buf):
                s = buf.strip()
                if s:
                    stmts.append(s)
                buf = ""
        self.assertEqual(len(stmts), 4)
        results = [self.conn.execute(s).fetchall() for s in stmts]
        self.assertEqual([r[0][0] for r in results], ["TRUNG", "VIET_THUONG", "TRONG", "NGUOI_LA"])
