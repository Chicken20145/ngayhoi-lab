# Chỉ số điểm danh sự kiện IT
- Nguồn dữ liệu: CSV giả lập khóa học (synthetic course CSV: dang_ky.csv, diem_danh.csv).
- Mục đích & vai trò: Báo cáo ban tổ chức; vai trò chịu trách nhiệm: Bộ phận IT / Phân tích dữ liệu.
- Tử số (A): Số lượt (ma_sv, UPPER(ma_phien)) duy nhất đã đăng ký có >= 1 lần quét hợp lệ. Quy tắc: loại quét trùng, chuẩn hóa chữ hoa mã phiên, loại quét chưa đăng ký. Ô phut_tre trống vẫn tính có mặt nhưng không suy ra đúng giờ.
- Mẫu số (B): Tổng số dòng đăng ký trong dang_ky.
- Tính tay bộ dữ liệu nhỏ (trước khi tính toàn bộ): A = 2 ({A, B}), B = 4 ({A, B, C, D}) -> Tỷ lệ = A/B = 2/4 = 50.0%.
