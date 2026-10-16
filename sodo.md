# Sơ đồ cổng đăng ký sau bài 4

```mermaid
flowchart TD
  A[Form Vite localhost 5173] -->|POST ma_sv và ma_phien| B[FastAPI localhost 8000]
  B --> C{Pydantic kiểm tra dữ liệu}
  C -->|Sai dữ liệu| D[422]
  C -->|Hợp lệ| E[INSERT SELECT với COUNT của đúng phiên nhỏ hơn 30]
  E -->|Ghi được một dòng| F[201 ok true]
  E -->|Vi phạm UNIQUE| G[409 DA_DANG_KY]
  E -->|Không ghi dòng nào| H{Kiểm tra cặp sinh viên và phiên trong cùng giao dịch}
  H -->|Đã tồn tại| G
  H -->|Chưa tồn tại| I[409 HET_CHO]
  F --> J[Thông báo thành công]
  G --> K[Thông báo đã đăng ký]
  I --> L[Thông báo phiên đủ 30 chỗ]
```

SQLite giữ bảng dang_ky với UNIQUE(ma_sv, ma_phien). Mỗi yêu cầu có một kết nối riêng. Không đếm chỗ ở frontend. Khi INSERT không thêm dòng vì hết chỗ, cần kiểm tra lại cặp đăng ký để vẫn ưu tiên thông báo DA_DANG_KY.
