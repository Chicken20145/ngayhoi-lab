# Cổng đăng ký Ngày hội việc làm

Bài tập môn **CSE3051 Các công cụ trong AI**, xây dựng cổng đăng ký phiên tham gia Ngày hội việc làm bằng FastAPI, SQLite và giao diện Vite.

## Chức năng

- Đăng ký bằng mã sinh viên và mã phiên.
- Không nhận đăng ký trùng một sinh viên trong cùng một phiên.
- Giới hạn mỗi phiên 30 người, tính riêng từng phiên.
- Hiển thị kết quả đăng ký thành công, đã đăng ký, hết chỗ và lỗi dữ liệu.
- Chạy kiểm thử tự động trên GitHub khi mở hoặc cập nhật pull request.

Ứng dụng phục vụ thực hành cục bộ, chưa có đăng nhập hay xác thực sinh viên. Chỉ sử dụng mã giả như `SV_TEST_001`, không nhập dữ liệu cá nhân thật.

## Công nghệ

- Backend: Python 3.12, FastAPI, Pydantic, Uvicorn.
- Dữ liệu: SQLite với ràng buộc `UNIQUE(ma_sv, ma_phien)`.
- Frontend: HTML, CSS, JavaScript, Vite.
- Kiểm thử: pytest, FastAPI TestClient và bộ test của Node.js.
- Quản lý mã nguồn và CI: Git, GitHub, GitHub Actions.

## Cấu trúc dự án

```text
ngayhoi-lab/
├── backend/        # API, script thử đồng thời và test backend
├── frontend/       # Giao diện và test JavaScript
├── .github/        # Workflow CI và mẫu pull request
├── spec.md         # Đặc tả chức năng
├── sodo.md         # Sơ đồ xử lý
└── README.md
```

## Cài đặt và chạy

Cần Python 3.12, Node.js 22.12 trở lên và Git. Các lệnh dưới đây dùng PowerShell trên Windows.

### Lấy mã nguồn

```powershell
git clone https://github.com/Chicken20145/ngayhoi-lab.git
cd ngayhoi-lab
git switch gioi-han-cho
```

Trong lúc PR giới hạn chỗ chưa hợp nhất, `master` là mốc bài 3; nhánh `gioi-han-cho` chứa giới hạn 30 chỗ và CI. Sau khi PR được hợp nhất, có thể dùng `master`.

### Chạy backend

Từ thư mục gốc dự án:

```powershell
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --only-binary=:all: -r backend/requirements-test.txt
cd backend
& ..\.venv\Scripts\python.exe -m uvicorn main:app --host localhost --port 8000
```

Trang thử API: **http://localhost:8000/docs**. Dữ liệu mặc định ở `backend/ngayhoi.db`. Muốn dùng CSDL khác, đặt biến môi trường `DB_PATH` trước khi khởi động. Không xóa CSDL đang dùng để chạy lại thí nghiệm.

### Chạy frontend

Mở cửa sổ PowerShell khác tại thư mục gốc dự án:

```powershell
cd frontend
npm ci --ignore-scripts
npm run dev
```

Mở **http://localhost:5173**. Backend phải chạy ở cổng 8000. CORS chỉ cho phép địa chỉ giao diện này.

## API đăng ký

`POST /api/dang-ky` nhận dữ liệu:

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

Nếu sinh viên đã có trong một phiên đầy, hệ thống ưu tiên báo `DA_DANG_KY`. Việc đếm và ghi được thực hiện trong một câu lệnh SQLite để tránh nhận vượt sức chứa khi có yêu cầu đồng thời.

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

Mỗi lượt dùng mã phiên chưa có dữ liệu. Kết quả mong đợi: 30 phản hồi 201 và 10 phản hồi 409. Script không xóa dữ liệu.

## Quy trình GitHub

Workflow `test.yml` chạy test backend, test frontend và build giao diện trên mọi PR. Nhánh `master` yêu cầu các check thành công và một lượt duyệt từ tài khoản khác trước khi hợp nhất. Không sửa test để làm CI xanh hoặc bỏ qua bảo vệ nhánh.

Đặc tả chi tiết nằm trong `spec.md`. Các phần tiếp nối được tổ chức bằng nhánh và PR. Không đưa `.venv`, `node_modules`, tệp CSDL, thông tin đăng nhập hoặc dữ liệu cá nhân lên Git.

## Công cụ hỗ trợ

Ollama được dùng để hỗ trợ bản nháp ở các bài trước. Mã có hỗ trợ AI vẫn được soát lại và kiểm thử. Không cần chạy Ollama để sử dụng ứng dụng.
