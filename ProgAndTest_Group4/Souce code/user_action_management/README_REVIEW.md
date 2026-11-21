# Người 5 – Admin: đặt phòng, check-in/out, doanh thu, khách hàng

**Use case của bạn:** Manage booking, Check-in, Check-out, Add incidental charge, View revenue, Manage user

Gói này chỉ chứa **các file bạn phải review** (đã xóa mọi file không liên quan). Để chạy được chương trình hãy dùng dự án đầy đủ `hotel.zip`, rồi mở các file dưới đây trong đó.

## File của bạn
| Loại | File | Nội dung |
|---|---|---|
| Môi trường | `Procfile` | lệnh chạy gunicorn |
| Python | `controllers/admin_operations.py` | Admin: bookings, check-in / check-out / charges, revenue, users. |
| Python | `models/actors/admin_operations.py` | Admin operations: bookings, check-in / check-out, charges, revenue, users. |
| Python | `services/admin_booking_service.py` | Admin use cases on bookings: approve / reject, check-in, check-out, charges, revenue, create customer. |
| CSS | `static/css/admin.css` | ADMIN: sidebar + light-blue work panel |
| HTML | `templates/admin/_layout.html` | Layout shared by all admin pages: sidebar on the left, light-blue workspace on the right |
| HTML | `templates/admin/bookings.html` |  |
| HTML | `templates/admin/revenue.html` |  |
| HTML | `templates/admin/user_new.html` |  |
| HTML | `templates/admin/users.html` |  |
| Test | `tests/conftest.py` |  |
| Test | `tests/helpers.py` | Small helpers shared by all test files (sign in as customer/admin, book a room, finish a stay, …). |
| Test | `tests/test_p5_admin_ops.py` | Person 5 – Admin operations: approve, check-in / out, charges, revenue, users.   Run:  pytest tests/test_p5_admin_ops.py -v |
| Môi trường | `wsgi.py` |  |

## Liên kết sang file của người khác (không có trong gói này)
- `templates/admin/_layout.html` (của bạn) được các trang của Người 6 dùng chung
- `services/booking_service.py`, `models/booking.py` – lõi và thực thể `Booking/Payment/Invoice` (Người 3)
- `templates/base.html` – mục "⚙ Management" ở navbar (Người 6)
- `controllers/admin_catalog.py` – cùng blueprint `admin_bp` (Người 6)

## Cách làm việc
1. Trong dự án đầy đủ: `pip install -r requirements.txt` rồi `python app.py` (http://localhost:5000).
2. Chạy test của bạn: `pytest tests/test_p5_*.py -v`.
3. Review theo luồng: template (HTML) → controller → actor → service → repository (SQL); đối chiếu use case ở `docs/TRACEABILITY.md`.
4. Mỗi lỗi tìm thấy: tạo GitHub Issue, sửa bằng Pull Request, chạy lại test.
5. Viết test case vào **Testing Document Template** của giảng viên (xem `docs/TASK_ASSIGNMENT.md`).
