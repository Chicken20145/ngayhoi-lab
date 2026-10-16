# Giới hạn chỗ mỗi phiên

Mỗi phiên nhận tối đa 30 sinh viên. Hai phiên được đếm riêng. Giữ API và dữ liệu của bài 3: POST `/api/dang-ky` với `ma_sv` và `ma_phien`.

| STT | Đang có | Hành động | Kết quả |
| --- | --- | --- | --- |
| 1 | P01 trống | SV000 đăng ký P01 | 201, `{"ok":true}` |
| 2 | P01 có 29 người | SV029 đăng ký P01 | 201, `{"ok":true}` |
| 3 | P01 có 30 người | SV030 đăng ký P01 | 409, `{"detail":"HET_CHO"}` |
| 4 | P01 có 30 người, gồm SV000 | SV000 đăng ký lại P01 | 409, `{"detail":"DA_DANG_KY"}` |
| 5 | P01 có 30 người, P02 trống | SV000 và SV030 lần lượt đăng ký P02 | Cả hai nhận 201; P01 không đổi |
| 6 | Một phiên mới trống | 40 sinh viên khác nhau gửi cùng lúc | 30 phản hồi 201, 10 phản hồi 409 HET_CHO; CSDL có đúng 30 dòng |

Đăng ký trùng được ưu tiên báo `DA_DANG_KY`, kể cả khi phiên đã đầy. Dữ liệu thiếu, rỗng hoặc sai kiểu vẫn trả 422 như bài 3. CORS chỉ cho phép `http://localhost:5173`.

Ngoài phạm vi: hủy đăng ký, đổi phiên, xác thực sinh viên và triển khai sự kiện thật.

## Cách kiểm tra

Năm test trong `backend/tests/test_gioi_han.py` tương ứng dòng 1–5, mỗi test dùng một tệp SQLite tạm riêng. Không dùng mock cho API hoặc CSDL. Dòng 6 kiểm tra riêng bằng `backend/ban_dong_thoi.py` qua máy chủ HTTP thật.

Chạy test trước khi sửa giới hạn: phải có 4 test qua và 1 test trượt ở người thứ 31. Commit test rồi giữ nguyên toàn bộ thư mục tests. Sau khi sửa, cả 5 test phải qua.

Trong thí nghiệm đồng thời, đặt tạm `time.sleep(0.05)` ngay trước INSERT. Chạy bản đếm rồi ghi riêng để quan sát lỗi, sau đó gộp đếm và ghi vào một INSERT có điều kiện. Hai lượt sửa đúng phải cho 30/10 với phiên mới, kể cả khi còn sleep. Bỏ sleep trước commit cuối.
