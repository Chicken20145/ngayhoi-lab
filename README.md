# Cổng đăng ký Ngày hội việc làm — bản thực hành công khai

Ứng dụng học tập chạy cục bộ, không có xác thực và không dùng cho sự kiện thật.
Chỉ nhập mã giả như `SV_TEST_001`, không dùng thông tin cá nhân.

## Chạy máy chủ

Cần Python 3.12. Từ thư mục kho mã:

```powershell
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
cd backend
& ..\.venv\Scripts\python.exe -m uvicorn main:app --host localhost --port 8000
```

Thử API tại http://localhost:8000/docs. CSDL demo chỉ lưu trên máy và không đưa lên Git.
Giao diện: mở cửa sổ khác, `cd frontend`, `npm ci --ignore-scripts`, `npm run dev`.
Địa chỉ giao diện là http://localhost:5173; giữ nguyên CORS giới hạn địa chỉ này.

## Riêng tư và lịch sử

Đây là lịch sử công khai được tái dựng từ các mốc bài trước, không phải các SHA gốc.
Tác giả commit dùng danh tính quy ước; các fixture là mã giả. Không nhập lịch sử Git gốc,
tài liệu Word, ảnh, log, bundle, CSDL hay thông tin người học vào kho này.
Phần bài 3–4 từng có bản nháp hỗ trợ bởi Ollama, được kiểm tra lại bằng test.

## Bài 4: giới hạn 30 chỗ

Mỗi phiên tối đa 30 người. Trùng cặp trả `DA_DANG_KY`; phiên đầy trả `HET_CHO`.
`spec.md` có sáu ví dụ; năm test giới hạn nằm trong `backend/tests/test_gioi_han.py`.

```powershell
& .\.venv\Scripts\python.exe -m pip install -r backend/requirements-test.txt
cd backend
& ..\.venv\Scripts\python.exe -m pytest -q
```

Hai commit test và tính năng tách riêng; test giới hạn không bị sửa sau commit test.
