# Báo cáo Bài 8 - Dữ liệu và phân tích có kiểm chứng

Học phần CSE3051. Ngày thực hiện: 06/11/2026. Nguồn: dữ liệu giả lập buoi-08 trong bộ tài liệu thực hành được phát, giữ nguyên byte CSV. Yêu cầu đối chiếu: slide 08 và hướng dẫn thực hành trang 91-100.

## 1. Định nghĩa được chọn trước khi tính

Theo `chi_so.md`, báo cáo **tỷ lệ lượt đăng ký có ít nhất một lần quét mã**, dùng cho ban tổ chức. Tử số là cặp sinh viên-phiên đã đăng ký, có quét, đếm một lần; mẫu số là số lượt đăng ký. Mã phiên được chuẩn hóa chữ hoa khi đối chiếu. Quét trùng không tăng tử số; người chưa đăng ký bị loại. Phút đến muộn trống vẫn là có đến, nhưng không được suy ra đúng giờ. Bộ phận IT chịu trách nhiệm chỉ số.

Chỉ số này không dùng để tự động cộng điểm rèn luyện: việc đó cần quy tắc đúng giờ và đủ số phiên khác.

## 2. Kiểm trên tập nhỏ có đáp án tính tay

Có bốn đăng ký A, B, C, D cho P01. Bốn lần quét: A hai lần, B dùng `p01`, E chưa đăng ký. Hai cặp hợp lệ là A-P01 và B-P01: **2/4 = 50%**. Phút trống trong tập nhỏ vẫn được tính có đến theo định nghĩa.

Chạy `mini.sql` trên DB mới riêng rồi chạy `ty_le.sql` trả `attended=2, registered=4, percent=50.0`. Bản sai `COUNT(*) FROM diem_danh` trả 4/4 = 100%. Có log và ảnh hiển thị log lệnh thực tế trong `bang-chung/`; các test cũng chạy tập nhỏ trong bộ nhớ.

## 3. Hồ sơ dữ liệu phát sẵn

Nạp đúng **245 lượt đăng ký** và **165 dòng quét**; giữ mã sinh viên dạng văn bản, không mở/lưu lại bằng Excel.

| Phép kiểm | Kết quả thực tế |
|---|---|
| Cặp quét trùng sau chuẩn hóa | 3 cặp, mỗi cặp 2 dòng: 22020005-P04, 22020031-P06, 22020044-P01 |
| Mã phiên viết thường | 1 dòng: 22020031-p06 |
| Phút đến muộn trống | 1 dòng: 22020044-P01 |
| Quét không có đăng ký tương ứng | 1 dòng: 22029999-P04 |

Các mã trên đều là dữ liệu giả lập được phát. JOIN chuẩn hóa `UPPER` nên không coi dòng `p06` là người lạ. Các loại lỗi có thể chồng trên cùng một cặp, không cộng số loại thành số người.

## 4. SQL đúng và bản sai minh họa

| Dữ liệu | Bản đếm toàn bộ lần quét | Theo định nghĩa đã viết |
|---|---:|---:|
| Tập nhỏ | 4/4 = 100% | 2/4 = 50% |
| CSV phát sẵn | 165/245 = 67,3469% | **161/245 = 65,7143%** |

Chênh lệch trên CSV là **1,6327 điểm phần trăm**: ba lượt quét dư do trùng và một lượt của người chưa đăng ký. Nếu chỉ nhìn số tổng, sai lệch nhỏ khó nhận ra; tập nhỏ làm lỗi lộ rõ.

`ty_le_ai.sql` là bản sai có chủ ý được giữ từ ví dụ trong slide để đối chiếu, không được dùng làm số báo cáo chính. Không coi đây là bằng chứng rằng một cuộc hội thoại AI thực tế đã sai đúng ba lần như ảnh minh họa của đề.

SQL đúng chọn `DISTINCT` trên **hai cột** của cặp, không ghép chuỗi làm khóa vì có thể va chạm. Mẫu số bằng 0 trả NULL, không suy diễn thành tỷ lệ 0%.

## 5. Kết quả theo phiên

| Phiên | Lượt đăng ký n | Có quét, bỏ trùng | Tỷ lệ |
|---|---:|---:|---:|
| P01 | 35 | 16 | 45,7143% |
| P02 | 27 | 18 | 66,6667% |
| P03 | 38 | 26 | 68,4211% |
| P04 | 23 | 18 | 78,2609% |
| P05 | 28 | 19 | 67,8571% |
| P06 | 33 | 18 | 54,5455% |
| P07 | 27 | 18 | 66,6667% |
| P08 | 34 | 28 | 82,3529% |
| Tổng | 245 | 161 | 65,7143% |

P08 cao nhất, P01 thấp nhất. Tổng được tính bằng tổng lượt có quét chia tổng đăng ký, không lấy trung bình đơn giản tám phần trăm. `bieu_do.png` dùng trục 0-100%, ghi n dưới từng cột, có tử số/mẫu số, định nghĩa và nguồn ngay trên hình.

## 6. Kiểm chứng và giới hạn

13 test độc lập qua: xử lý tập nhỏ, bốn loại lỗi, khóa cặp không va chạm, phiên không có người đến, mẫu số rỗng, giữ nguyên văn bản CSV, kiểm header, không ghi đè DB, chỉ đọc và tách SQL có dấu chấm phẩy trong chuỗi. Đã chạy lại từ gói giải nén riêng theo README.

Không sửa CSV hoặc đáp án để khớp số trong tài liệu. Kết quả phản ánh dữ liệu mô phỏng và định nghĩa đã chọn; không kết luận tỷ lệ tham dự của sự kiện thật, không khẳng định người quét ở lại hết phiên và không dùng số này để xét điểm.

## 7. Trả lời câu hỏi tự kiểm tra

**45% và 86%, số nào đúng?** Cả hai có thể đúng nhưng trả lời khác câu hỏi: tỷ lệ lượt đến đúng giờ và tỷ lệ người có đến ít nhất một lần. Cần thống nhất mục đích, đơn vị đếm, tử/mẫu, loại trừ và người chịu trách nhiệm trước khi so sánh báo cáo.

**Cách kiểm SQL của AI?** Đáp án B: chạy trên tập nhỏ đã tính tay, có lỗi trùng/khác kiểu chữ/người lạ. Chạy nhiều lần hoặc thấy số trong 0-100% không chứng minh SQL đúng.
