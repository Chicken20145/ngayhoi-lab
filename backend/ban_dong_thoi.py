"""Gửi 40 đăng ký thật qua HTTP; không xóa hay tạo trước dữ liệu."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def run(session, url, database=None):
    if database is not None:
        if not database.is_file():
            raise ValueError('Không tìm thấy CSDL của server.')
        with closing(sqlite3.connect(database)) as db:
            count = db.execute('SELECT COUNT(*) FROM dang_ky WHERE ma_phien = ?',
                               (session,)).fetchone()[0]
        if count:
            raise ValueError('Phiên đã có dữ liệu. Chọn mã phiên mới, không xóa dữ liệu cũ.')

    barrier = threading.Barrier(40, timeout=20)
    origin = time.perf_counter()

    def send(i):
        student = f'TN{i:03}'
        request = Request(url, json.dumps({'ma_sv': student, 'ma_phien': session}).encode(),
                          {'Content-Type': 'application/json'}, method='POST')
        barrier.wait()
        start = time.perf_counter() - origin
        try:
            try:
                response = urlopen(request, timeout=25)
            except HTTPError as error:
                response = error
            with response:
                status = response.status
                raw = response.read().decode('utf-8')
            try:
                body = json.loads(raw)
            except json.JSONDecodeError:
                body = {'invalid_json': raw}
            return {'ma_sv': student, 'status': status, 'body': body,
                    'start_s': round(start, 6),
                    'end_s': round(time.perf_counter() - origin, 6)}
        except (URLError, TimeoutError, OSError) as error:
            return {'ma_sv': student, 'status': 0, 'error': str(error),
                    'start_s': round(start, 6),
                    'end_s': round(time.perf_counter() - origin, 6)}

    with ThreadPoolExecutor(max_workers=40) as pool:
        records = list(pool.map(send, range(40)))
    counts = Counter(record['status'] for record in records)
    result = {'utc': datetime.now(timezone.utc).isoformat(), 'session': session,
              'url': url, 'workers': 40, 'requests': records,
              'counts': {str(key): value for key, value in sorted(counts.items())},
              'start_spread_s': round(max(r['start_s'] for r in records) -
                                      min(r['start_s'] for r in records), 6),
              'all_started_before_first_response': max(r['start_s'] for r in records) <
                                                   min(r['end_s'] for r in records)}
    valid = all((r['status'] == 201 and r.get('body') == {'ok': True}) or
                (r['status'] == 409 and r.get('body') == {'detail': 'HET_CHO'})
                for r in records)
    result['valid_response_bodies'] = valid
    if database is not None:
        with closing(sqlite3.connect(database)) as db:
            saved = {row[0] for row in db.execute(
                'SELECT ma_sv FROM dang_ky WHERE ma_phien = ?', (session,))}
        result['database_rows'] = len(saved)
        result['persisted_matches_201'] = saved == {
            r['ma_sv'] for r in records if r['status'] == 201}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('session', help='Mã phiên mới chưa có dữ liệu')
    parser.add_argument('--url', default='http://localhost:8000/api/dang-ky')
    parser.add_argument('--database', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--expect-capacity', action='store_true')
    args = parser.parse_args()
    if not args.session.strip() or len(args.session.strip()) > 64:
        parser.error('Mã phiên phải từ 1 đến 64 ký tự.')
    result = run(args.session.strip(), args.url, args.database)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"{result['session']} 201: {result['counts'].get('201', 0)}; "
          f"409: {result['counts'].get('409', 0)}; CSDL: {result.get('database_rows', 'chua kiem tra')}")
    print(f"40 threads; spread: {result['start_spread_s']}s; "
          f"JSON hop le: {result['valid_response_bodies']}")
    if not result['valid_response_bodies'] or not result.get('persisted_matches_201', True):
        raise SystemExit('Thí nghiệm không hợp lệ: kiểm tra lỗi và CSDL trong JSON.')
    if args.expect_capacity and (result['counts'] != {'201': 30, '409': 10} or
                                result.get('database_rows', 30) != 30):
        raise SystemExit('Chưa đạt giới hạn 30 chỗ.')


if __name__ == '__main__':
    main()
