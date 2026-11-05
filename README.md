# Cổng đăng ký Ngày hội việc làm

Bài tập môn **CSE3051 Các công cụ trong AI**, xây dựng cổng đăng ký phiên tham gia Ngày hội việc làm bằng FastAPI, SQLite và giao diện Vite, kèm theo các mô-đun dòng lệnh (CLI) riêng biệt cho Bài 6 (RAG quy chế) và Bài 7 (Trợ lý tác vụ).

## Chức năng

- Đăng ký bằng mã sinh viên và mã phiên.
- Không nhận đăng ký trùng một sinh viên trong cùng một phiên.
- Giới hạn mỗi phiên 30 người, tính riêng từng phiên.
- Xem số chỗ còn lại của một phiên qua API `GET /api/con-cho`.
- Bài 6: Mô-đun RAG tra cứu quy chế (`bge-m3` embedding, `qwen2.5:3b` sinh văn bản) chạy qua dòng lệnh (CLI).
- Bài 7: Trợ lý tác vụ tự động CLI với định danh mẫu cố định `SV_DEMO_001`, thao tác giới hạn phiên P01-P03, yêu cầu xác nhận chính xác ký tự `'c'` trước khi ghi, không hỗ trợ hủy phiên.
- Các mô-đun RAG và trợ lý tác vụ là các script dòng lệnh riêng biệt, hiện chưa kết nối vào giao diện web FastAPI.
- Chạy kiểm thử tự động trên GitHub qua `labs.yml` và `test.yml` khi mở hoặc cập nhật pull request.

Ứng dụng phục vụ thực hành cục bộ, chưa có đăng nhập hay xác thực sinh viên. Chỉ sử dụng mã giả như `SV_TEST_001` hoặc `SV_DEMO_001`, không nhập dữ liệu cá nhân thật.

## Công nghệ

- Backend đăng ký: Python 3.12, FastAPI, Pydantic, Uvicorn.
- Dữ liệu: SQLite với ràng buộc `UNIQUE(ma_sv, ma_phien)`.
- Giao diện: HTML, CSS, JavaScript, Vite.
- Mô-đun AI (Bài 6 & Bài 7): Python, Ollama (`qwen2.5:3b`, `bge-m3`), công cụ nhúng cục bộ.
- Kiểm thử: pytest, FastAPI TestClient, Python `unittest`.
- Quản lý mã nguồn và CI: Git, GitHub, GitHub Actions.

## Cấu trúc dự án

```text
ngayhoi-lab/
├── backend/        # API, script thử đồng thời và test backend
├── frontend/       # Giao diện và test JavaScript
├── bai6-quyche/    # Mô-đun RAG tra cứu quy chế (CLI, nhung.py, tim.py, hoi.py, danh_gia.py)
├── bai7-agent/     # Trợ lý tác vụ dòng lệnh (agent.py)
├── .github/        # Workflow CI (labs.yml, test.yml) và mẫu pull request
├── spec.md         # Đặc tả chức năng
├── sodo.md         # Sơ đồ xử lý
└── README.md
```

Kho lưu trữ công khai không chứa tệp dữ liệu cục bộ như `quy_che.md`, `cau_hoi_vang.json`, `chi_muc.json`, `nhiem_vu.json`, `nhat_ky.jsonl`. Người dùng cần tự chuẩn bị dữ liệu cục bộ và chạy script `nhung.py` để xây dựng chỉ mục. Ollama là bắt buộc khi chạy các mô-đun AI (Bài 6 và Bài 7), không bắt buộc cho chức năng đăng ký cơ bản.

## Cài đặt và chạy

Cần Python 3.12, Node.js 22.12 trở lên và Git. Các lệnh dưới đây dùng PowerShell trên Windows tại thư mục gốc dự án trên nhánh `master`.

### Lấy mã nguồn

```powershell
git clone https://github.com/Chicken20145/ngayhoi-lab.git
cd ngayhoi-lab
```

### Chạy backend đăng ký

Từ thư mục gốc dự án:

```powershell
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --only-binary=:all: -r backend/requirements-test.txt
cd backend
& ..\.venv\Scripts\python.exe -m uvicorn main:app --host localhost --port 8000
```

Trang thử API: **http://localhost:8000/docs**. Dữ liệu mặc định ở `backend/ngayhoi.db`. Muốn dùng CSDL khác, đặt biến môi trường `DB_PATH` trước khi khởi động. Không xóa CSDL đang dùng (`backend/ngayhoi.db`) để chạy lại thí nghiệm.

### Chạy frontend

Mở cửa sổ PowerShell khác tại thư mục gốc dự án:

```powershell
cd frontend
npm ci --ignore-scripts
npm run dev
```

Mở **http://localhost:5173**. Backend phải chạy ở cổng 8000. CORS chỉ cho phép địa chỉ giao diện `http://localhost:5173`.

## API

### POST /api/dang-ky

Nhận dữ liệu JSON:

```json
{
  "ma_sv": "SV_TEST_001",
  "ma_phien": "P01"
}
```

| Trường hợp | HTTP | Phản hồi |
| --- | --- | --- |
| Đăng ký thành công | 201 | `{"ok": true}` |
| Đã đăng ký phiên này | 409 | `{"detail": "DA_DANG_KY"}` |
| Phiên đã đủ 30 người | 409 | `{"detail": "HET_CHO"}` |
| Dữ liệu không hợp lệ | 422 | Chi tiết lỗi kiểm tra dữ liệu |
| Lỗi cơ sở dữ liệu | 500 | `{"detail": "LOI_CSDL"}` |

Nếu sinh viên đã có trong một phiên đầy, hệ thống ưu tiên báo `DA_DANG_KY`. Việc đếm và ghi được thực hiện trong một câu lệnh SQLite nguyên tử để tránh nhận vượt sức chứa khi có yêu cầu đồng thời.

### GET /api/con-cho

Gọi `GET /api/con-cho?ma_phien=P01` để nhận `{"con_cho": n}`. Phiên chưa có đăng ký trả 30; phiên đầy trả 0. API chỉ đọc, không giữ chỗ. Mã phiên thiếu hoặc không hợp lệ trả 422; lỗi CSDL trả 500.

## Kiểm thử

Từ thư mục gốc dự án:

```powershell
cd backend
& ..\.venv\Scripts\python.exe -m pytest -q
cd ../frontend
npm test
npm run build
```

Test backend dùng tệp SQLite tạm riêng, không dùng CSDL demo. Năm test trong `backend/tests/test_gioi_han.py` kiểm tra phiên trống, người thứ 30, người thứ 31, đăng ký trùng khi đầy và đếm riêng từng phiên.

Để thử 40 yêu cầu đồng thời, giữ backend đang chạy và mở cửa sổ khác tại `backend`:

```powershell
& ..\.venv\Scripts\python.exe ban_dong_thoi.py P_THU_MOI --expect-capacity
```

Mỗi lượt dùng mã phiên chưa có dữ liệu (thay đổi mã phiên mới cho mỗi lần chạy). Kết quả mong đợi: 30 phản hồi 201 và 10 phản hồi 409. Script không xóa dữ liệu.

Chạy kiểm thử các mô-đun lab (từ thư mục gốc dự án, cài đặt phụ thuộc AI bao gồm `requests` và `numpy` vào `.venv`, sau đó chạy unittest):

```powershell
& .\.venv\Scripts\python.exe -m pip install --only-binary=:all: -r bai6-quyche/requirements.txt -r bai7-agent/requirements.txt
& .venv\Scripts\python.exe -X utf8 -m unittest discover -s bai6-quyche/tests -v
& .venv\Scripts\python.exe -X utf8 -m unittest discover -s bai7-agent/tests -v
```

## Quy trình GitHub

Workflow `labs.yml` và `test.yml` chạy test backend, test frontend, build giao diện và kiểm thử lab tự động trên mọi PR và push lên `master`. Nhánh `master` yêu cầu các check CI thành công; trong dự án solo không yêu cầu phê duyệt từ tài khoản khác. Không bỏ qua bảo vệ nhánh hoặc sửa test để làm CI xanh.

Đặc tả chi tiết nằm trong `spec.md`. Không đưa `.venv`, `node_modules`, tệp CSDL, thông tin đăng nhập hoặc dữ liệu cá nhân lên Git.

## Công cụ hỗ trợ

Ollama được dùng để hỗ trợ chạy mô hình LLM cục bộ cho Bài 6 và Bài 7. Không cần chạy Ollama để sử dụng chức năng đăng ký cơ bản của ứng dụng.
