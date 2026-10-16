"""Năm ví dụ trong spec.md; bản nháp Ollama, đã sửa trước commit test."""
import pytest
from fastapi.testclient import TestClient

from main import create_app


@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(tmp_path / 'test.db')) as test_client:
        yield test_client


def fill(client, n, ma_phien='P01'):
    for i in range(n):
        response = client.post('/api/dang-ky', json={
            'ma_sv': f'SV{i:03}', 'ma_phien': ma_phien,
        })
        assert response.status_code == 201
        assert response.json() == {'ok': True}


def test_phien_trong_cho_phep_dang_ky(client):
    response = client.post('/api/dang-ky', json={'ma_sv': 'SV000', 'ma_phien': 'P01'})
    assert response.status_code == 201
    assert response.json() == {'ok': True}


def test_nguoi_thu_30_duoc_nhan(client):
    fill(client, 29)
    response = client.post('/api/dang-ky', json={'ma_sv': 'SV029', 'ma_phien': 'P01'})
    assert response.status_code == 201
    assert response.json() == {'ok': True}


def test_nguoi_thu_31_bi_tu_choi(client):
    fill(client, 30)
    response = client.post('/api/dang-ky', json={'ma_sv': 'SV030', 'ma_phien': 'P01'})
    assert response.status_code == 409
    assert response.json() == {'detail': 'HET_CHO'}


def test_trung_uu_tien_khi_phien_day(client):
    fill(client, 30)
    response = client.post('/api/dang-ky', json={'ma_sv': 'SV000', 'ma_phien': 'P01'})
    assert response.status_code == 409
    assert response.json() == {'detail': 'DA_DANG_KY'}


def test_gioi_han_tinh_rieng_tung_phien(client):
    fill(client, 30)
    for student in ('SV000', 'SV030'):
        response = client.post('/api/dang-ky', json={'ma_sv': student, 'ma_phien': 'P02'})
        assert response.status_code == 201
        assert response.json() == {'ok': True}
