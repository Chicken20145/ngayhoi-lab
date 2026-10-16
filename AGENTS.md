# Quy tắc làm việc trong dự án

- Giữ nguyên các quy tắc của người dùng ở cấp điều phối; tệp này chỉ giới hạn công việc trong kho mã.
- Phạm vi phần còn chỗ: `backend/main.py`, test mới và tài liệu liên quan.
- Không sửa test cũ, đặc biệt `backend/tests/test_gioi_han.py`; không đổi frontend hoặc `.github` trong PR tính năng backend.
- Viết test trước, xác nhận đỏ vì thiếu hành vi, rồi sửa mã và chạy lại toàn bộ test.
- GET chỉ đọc CSDL, dùng SQL tham số; không tạo bảng, ghi dữ liệu hoặc đổi quy tắc POST và CORS.
- Giữ diff tính năng dưới 200 dòng; dừng và báo nếu cần mở rộng phạm vi.
- Không đưa dữ liệu cá nhân, CSDL, token hoặc thông tin đăng nhập vào kho.
- Từ `backend`, chạy `python -m pytest -q`; không bỏ hoặc sửa test để làm xanh.
- Worker chỉ tạo diff và báo cáo; điều phối viên soát và chạy lại test trước khi commit hoặc push trong tác vụ đã được người dùng ủy quyền.
- Không tự động Approve, merge hoặc bỏ qua quy tắc bảo vệ nhánh.
