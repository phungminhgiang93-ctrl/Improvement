
# 4M Internal Reporting System - Desktop GUI

Phiên bản chạy thử **không dùng Streamlit, không dùng Flask/FastAPI**.
Giao diện native Windows bằng Tkinter/ttk.

## Chạy

Yêu cầu Python 3.10+.

```powershell
py main.py
```

hoặc double-click:

```text
run_gui.bat
```

Không cần `pip install`.

## Tài khoản demo

- E001 — Leader — Tổ A
- E002 — Trưởng nhóm/Kỹ sư — Tổ A
- E003 — Trưởng phòng
- E004 — Leader — Tổ B
- E005 — Trưởng nhóm/Kỹ sư — Tổ B

## Kiến trúc

```text
main.py
database.py
gui/
    app_window.py
    dashboard_frame.py
    report_frame.py
    management_frame.py
    notice_frame.py
engines/
    man_engine.py
    method_engine.py
    material_engine.py
    machine_engine.py
config/
    employees.csv
    machines.csv
    bom_list.csv
    wi_list.csv
data/
    4m_system.db
attachments/
```

## Luồng

Leader:
Đăng nhập → Báo cáo 4M → chọn Man/Method/Material/Machine → Submit.

Trưởng nhóm/Kỹ sư:
Xem báo cáo phạm vi phụ trách → cập nhật trạng thái → phản hồi/chuyển giao.

Trưởng phòng:
Xem toàn bộ → cập nhật → phê duyệt → phát hành và ghim chỉ thị.

## Database

SQLite được đặt trong `data/4m_system.db` và tự tạo khi chạy lần đầu.

Có `audit_logs` để lưu lịch sử:
- tạo báo cáo
- cập nhật trạng thái
- phản hồi
- phê duyệt

## Giai đoạn tiếp theo

Các engine hiện đã tách riêng để có thể thay bằng logic nghiệp vụ thật mà không cần viết lại GUI.

Nên phát triển tiếp:
1. Luồng giao việc và PIC.
2. Deadline/SLA.
3. Cảnh báo sự cố mức Cao.
4. Dashboard KPI 4M.
5. Import Excel master tự động.
6. Folder W.I thật trên server.
7. BOM theo version/effective date.
8. Quyền theo khu vực/dây chuyền/tổ.
9. Mở file đính kèm trực tiếp.
10. Đồng bộ database khi chuyển từ bản thử nghiệm sang hệ thống mạng nhiều người dùng.
