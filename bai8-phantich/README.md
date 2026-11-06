# Bài 8: Dữ liệu và phân tích có kiểm chứng

Dữ liệu giả lập của học phần CSE3051, không phải dữ liệu sinh viên thật. Mã nguồn không dùng CSDL đăng ký của ứng dụng web.

## Chạy trong gói nộp đã giải nén

Cần Python 3.11+; riêng biểu đồ cần `python -m pip install -r requirements.txt`.

```powershell
python -X utf8 -m unittest discover -s . -p "test_*.py" -v
python chay.py mini.sql --database mini.db --init
python chay.py ty_le.sql --database mini.db
python chay.py ty_le_ai.sql --database mini.db
python nap.py --data du_lieu --database phan_tich.db
python chay.py ho_so.sql --database phan_tich.db
python chay.py ty_le.sql --database phan_tich.db
python chay.py ty_le_ai.sql --database phan_tich.db
python chay.py theo_phien.sql --database phan_tich.db
python ve.py --database phan_tich.db --output bieu_do.png
```

Kỳ vọng: 13 test qua; tập nhỏ `2 | 4 | 50.0`; dữ liệu phát sẵn `161 | 245 | 65.7143`. Bản đếm sai cho 100% ở tập nhỏ và 67,3469% ở dữ liệu phát sẵn.

`--init` và `nap.py` chỉ tạo CSDL mới, từ chối ghi đè tệp đã có. Khi chạy lại phần tạo, dùng tên DB mới; các lệnh SELECT có thể chạy lại trên DB cũ. Chạy truy vấn thường mở CSDL chỉ đọc, không ngầm tạo DB.

Trong checkout Git, hai CSV gốc nằm ở `../private-work/B8/du_lieu`; thay `--data du_lieu` bằng đường dẫn này. Trong ZIP nộp, dữ liệu đã nằm ngay trong `du_lieu/`.

## Nội dung nộp

- `chi_so.md`: định nghĩa trước khi tính; `mini.sql`: đáp án tính tay 2/4.
- `ho_so.sql` và bốn SQL riêng: trùng, viết thường, trống, không đăng ký.
- `ty_le.sql`, `ty_le_ai.sql`, `theo_phien.sql`: đúng, bản sai minh họa và theo phiên.
- `nap.py`, `chay.py`, `ve.py`, hai file test và `requirements.txt`.
- `bao_cao.md`, `bieu_do.png`, `bang-chung/`, `ket_qua.json`, `du_lieu/` nguyên bản.

Đổi `MaSV` trong tên ZIP thành mã sinh viên của người nộp. Không gửi `.venv`, `__pycache__`, `node_modules` hoặc DB tạm. Mở `bao_cao.md` để xem số thực đo và câu trả lời tự kiểm tra.
