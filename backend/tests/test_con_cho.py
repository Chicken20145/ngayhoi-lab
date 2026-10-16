"""Read-only remaining-capacity contract against real temporary SQLite files."""
from contextlib import closing
import sqlite3

import pytest
from fastapi.testclient import TestClient

from main import create_app


@pytest.fixture
def case(tmp_path):
    path = tmp_path / 'test.db'
    with TestClient(create_app(path)) as client:
        yield client, path


@pytest.mark.parametrize('count, expected', [(0, 30), (1, 29), (30, 0)])
def test_available_seats_at_boundaries(case, count, expected):
    client, _ = case
    for i in range(count):
        assert client.post('/api/dang-ky', json={
            'ma_sv': f'SV_TEST_{i:03}', 'ma_phien': 'P01',
        }).status_code == 201
    response = client.get('/api/con-cho', params={'ma_phien': 'P01'})
    assert response.status_code == 200
    assert response.json() == {'con_cho': expected}


def test_other_session_is_separate_and_get_does_not_add_rows(case):
    client, path = case
    assert client.post('/api/dang-ky', json={
        'ma_sv': 'SV_TEST_001', 'ma_phien': 'P01',
    }).status_code == 201
    assert client.get('/api/con-cho', params={'ma_phien': 'P02'}).json() == {'con_cho': 30}
    with closing(sqlite3.connect(path)) as db:
        assert db.execute('SELECT COUNT(*) FROM dang_ky').fetchone()[0] == 1


@pytest.mark.parametrize('query', [None, '', '   ', 'P' * 65])
def test_invalid_session_query_is_rejected(case, query):
    client, _ = case
    params = {} if query is None else {'ma_phien': query}
    assert client.get('/api/con-cho', params=params).status_code == 422


def test_trim_happens_before_normalized_length_validation(case):
    client, _ = case
    session = 'P' * 64
    assert client.post('/api/dang-ky', json={
        'ma_sv': 'SV_TEST_001', 'ma_phien': session,
    }).status_code == 201
    response = client.get('/api/con-cho', params={'ma_phien': f' {session} '})
    assert response.status_code == 200
    assert response.json() == {'con_cho': 29}


def test_sql_looking_session_is_data_not_a_filter(case):
    client, _ = case
    assert client.post('/api/dang-ky', json={
        'ma_sv': 'SV_TEST_001', 'ma_phien': 'P01',
    }).status_code == 201
    response = client.get('/api/con-cho', params={'ma_phien': "P01' OR '1'='1"})
    assert response.status_code == 200
    assert response.json() == {'con_cho': 30}
    assert client.get('/api/con-cho', params={'ma_phien': 'P01'}).json() == {'con_cho': 29}


def test_database_error_is_generic_and_get_never_recreates_schema(case):
    client, path = case
    with closing(sqlite3.connect(path)) as db, db:
        db.execute('DROP TABLE dang_ky')
    response = client.get('/api/con-cho', params={'ma_phien': 'P01'})
    assert response.status_code == 500
    assert response.json() == {'detail': 'LOI_CSDL'}
    with closing(sqlite3.connect(path)) as db:
        assert db.execute("SELECT name FROM sqlite_master WHERE name = 'dang_ky'").fetchone() is None


def test_legacy_overfull_session_never_returns_negative_seats(case):
    client, path = case
    with closing(sqlite3.connect(path)) as db, db:
        db.executemany('INSERT INTO dang_ky VALUES (?, ?)',
                       [(f'SV_TEST_{i:03}', 'P01') for i in range(31)])
    response = client.get('/api/con-cho', params={'ma_phien': 'P01'})
    assert response.status_code == 200
    assert response.json() == {'con_cho': 0}
