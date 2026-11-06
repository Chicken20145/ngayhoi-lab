# Sơ đồ xử lý đăng ký và xem chỗ

```mermaid
sequenceDiagram
    actor SV as Sinh viên
    participant UI as Giao diện
    participant API as FastAPI
    participant DB as SQLite
    SV->>UI: Nhập mã sinh viên, chọn phiên
    UI->>API: POST /api/dang-ky
    API->>API: Kiểm tra dữ liệu, bỏ khoảng trắng
    alt Dữ liệu không hợp lệ
        API-->>UI: 422
    else Dữ liệu hợp lệ
        API->>DB: INSERT có điều kiện COUNT đúng phiên < 30
        alt Thêm được một dòng
            DB-->>API: 1 dòng
            API-->>UI: 201, ok=true
            UI-->>SV: Đã đăng ký
        else Trùng hoặc không thêm dòng
            API->>DB: Kiểm tra cặp sinh viên-phiên nếu cần
            DB-->>API: Đã tồn tại hoặc hết chỗ
            API-->>UI: 409, DA_DANG_KY hoặc HET_CHO
            UI-->>SV: Đã đăng ký hoặc Hết chỗ
        end
    end
    Note over UI: Trạng thái từng sinh viên/phiên chỉ được nhớ trong trang đang mở
    opt Agent xem chỗ
        SV->>API: GET /api/con-cho?ma_phien=P01
        API->>DB: Kết nối mode=ro, SELECT COUNT có tham số
        DB-->>API: Số đăng ký của phiên
        API-->>SV: con_cho=max(0,30-count)
    end
```

UNIQUE(ma_sv,ma_phien) chặn trùng tại CSDL. COUNT nằm cùng câu INSERT để tránh nhận vượt 30 khi đồng thời. Đăng ký trùng được ưu tiên báo trước hết chỗ. GET chỉ là snapshot, không giữ chỗ, tạo bảng hay ghi dữ liệu. Lỗi SQLite trả LOI_CSDL, không lộ chi tiết.
