"""Tests use a real SQLite file per test, never the demo database."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
import importlib.util
from pathlib import Path
import sqlite3
import tempfile
import unittest

from fastapi.testclient import TestClient

MAIN = Path(__file__).resolve().parents[1] / 'main.py'


class RegistrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not MAIN.exists():
            raise AssertionError('Backend main.py chưa được triển khai')
        spec = importlib.util.spec_from_file_location('registration_main', MAIN)
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / 'test.db'
        self.app = self.module.create_app(self.path)
        self.client = TestClient(self.app)
        self.client.__enter__()
        self.addCleanup(self.client.__exit__, None, None, None)

    def post(self, **changes):
        return self.client.post('/api/dang-ky', json={
            'ma_sv': 'SV_TEST_001', 'ma_phien': 'P01', **changes,
        })

    def test_first_registration_creates_row_with_201(self):
        response = self.post()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {'ok': True})
        with closing(sqlite3.connect(self.path)) as db, db:
            self.assertEqual(db.execute('SELECT ma_sv, ma_phien FROM dang_ky').fetchall(),
                             [('SV_TEST_001', 'P01')])

    def test_duplicate_returns_409_without_second_row(self):
        self.post()
        response = self.post()
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json(), {'detail': 'DA_DANG_KY'})
        with closing(sqlite3.connect(self.path)) as db, db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM dang_ky').fetchone()[0], 1)

    def test_database_itself_rejects_duplicate_insert(self):
        self.post()
        with closing(sqlite3.connect(self.path)) as db, db:
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute('INSERT INTO dang_ky(ma_sv, ma_phien) VALUES (?, ?)',
                           ('SV_TEST_001', 'P01'))

    def test_missing_student_field_returns_422(self):
        self.assertEqual(self.client.post('/api/dang-ky', json={'ma_phien':'P01'}).status_code, 422)

    def test_missing_session_field_returns_422(self):
        self.assertEqual(self.client.post('/api/dang-ky', json={'ma_sv':'SV_TEST_001'}).status_code, 422)

    def test_blank_and_non_string_fields_return_422(self):
        for field in ('ma_sv', 'ma_phien'):
            for value in ('', '  ', None, 123, True, 'x' * 65):
                with self.subTest(field=field, value=value):
                    self.assertEqual(self.post(**{field:value}).status_code, 422)

    def test_trimmed_pair_is_also_duplicate(self):
        self.assertEqual(self.post(ma_sv=' SV_TEST_001 ', ma_phien=' P01 ').status_code, 201)
        self.assertEqual(self.post().status_code, 409)

    def test_same_student_can_register_other_session(self):
        self.post()
        self.assertEqual(self.post(ma_phien='P02').status_code, 201)

    def test_other_student_can_register_same_session(self):
        self.post()
        self.assertEqual(self.post(ma_sv='SV_TEST_002').status_code, 201)

    def test_reopening_app_preserves_registration(self):
        self.post()
        with TestClient(self.module.create_app(self.path)) as reopened:
            response = reopened.post('/api/dang-ky', json={'ma_sv':'SV_TEST_001','ma_phien':'P01'})
        self.assertEqual(response.status_code, 409)

    def test_sql_payload_is_stored_as_data(self):
        student = "x'); DROP TABLE dang_ky;--"
        self.assertEqual(self.post(ma_sv=student).status_code, 201)
        self.assertEqual(self.post(ma_sv=student).status_code, 409)
        self.assertEqual(self.post().status_code, 201)

    def test_concurrent_duplicate_has_one_winner(self):
        with ThreadPoolExecutor(max_workers=2) as pool:
            responses = list(pool.map(lambda _: self.post(), range(2)))
        self.assertEqual(sorted(r.status_code for r in responses), [201, 409])

    def test_allowed_cors_preflight(self):
        r = self.client.options('/api/dang-ky', headers={
            'Origin':'http://localhost:5173', 'Access-Control-Request-Method':'POST',
            'Access-Control-Request-Headers':'content-type',
        })
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.headers.get('access-control-allow-origin'), 'http://localhost:5173')

    def test_other_origins_not_allowed(self):
        for origin in ('https://example.com', 'http://localhost:5174', 'http://127.0.0.1:5173'):
            with self.subTest(origin=origin):
                r = self.client.options('/api/dang-ky', headers={
                    'Origin':origin, 'Access-Control-Request-Method':'POST',
                })
                self.assertEqual(r.status_code, 400)
                self.assertNotIn('access-control-allow-origin', r.headers)

    def test_allowed_origin_has_cors_on_success_and_conflict(self):
        for expected in (201, 409):
            r = self.client.post('/api/dang-ky', json={'ma_sv':'SV_TEST_001','ma_phien':'P01'},
                                 headers={'Origin':'http://localhost:5173'})
            self.assertEqual(r.status_code, expected)
            self.assertEqual(r.headers.get('access-control-allow-origin'), 'http://localhost:5173')

    def test_allowed_origin_has_cors_on_validation_error(self):
        r = self.client.post('/api/dang-ky', json={}, headers={'Origin':'http://localhost:5173'})
        self.assertEqual(r.status_code, 422)
        self.assertEqual(r.headers.get('access-control-allow-origin'), 'http://localhost:5173')

    def test_invalid_requests_insert_nothing(self):
        self.post(ma_sv=' ')
        self.post(ma_phien=None)
        with closing(sqlite3.connect(self.path)) as db, db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM dang_ky').fetchone()[0], 0)

    def test_unrelated_integrity_error_is_not_duplicate(self):
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute("CREATE TRIGGER reject_demo BEFORE INSERT ON dang_ky "
                       "BEGIN SELECT RAISE(ABORT, 'DEMO_OTHER_CONSTRAINT'); END;")
        with TestClient(self.app, raise_server_exceptions=False) as separate:
            r = separate.post('/api/dang-ky', json={'ma_sv':'SV_TEST_001','ma_phien':'P01'},
                              headers={'Origin':'http://localhost:5173'})
        self.assertEqual(r.status_code, 500)
        self.assertNotIn('DA_DANG_KY', r.text)
        self.assertEqual(r.headers.get('access-control-allow-origin'), 'http://localhost:5173')

    def test_docs_and_openapi_include_registration(self):
        self.assertEqual(self.client.get('/docs').status_code, 200)
        schema = self.client.get('/openapi.json').json()
        responses = schema['paths']['/api/dang-ky']['post']['responses']
        self.assertIn('201', responses)
        self.assertIn('409', responses)
        self.assertIn('422', responses)


if __name__ == '__main__':
    unittest.main()
