# Người 4 – Booking của tôi, hủy + hoàn tiền, thêm dịch vụ, đánh giá

**Use case của bạn:** View my bookings, Cancel booking, Refund payment, Review stay, Add extra service

Gói này chỉ chứa **các file bạn phải review** (đã xóa mọi file không liên quan). Để chạy được chương trình hãy dùng dự án đầy đủ `hotel.zip`, rồi mở các file dưới đây trong đó.

## File của bạn
| Loại | File | Nội dung |
|---|---|---|
| Môi trường | `.gitignore` | file không đưa lên Git |
| Python | `controllers/my_bookings.py` | My bookings, cancel (+ refund), add service, review. |
| Python | `models/actors/customer_after_booking.py` | Customer operations after booking: history, cancel, review, add service. |
| Môi trường | `models/mailer.py` | Simulated e-mail sender: appends every message to emails.log. |
| Python | `models/review.py` | Review entity + ReviewRepo. |
| Python | `services/after_booking_service.py` | Booking use cases after booking: cancel (+ refund), add service, review. |
| CSS | `static/css/after_booking.css` | AFTER BOOKING: cancel dialog, review form + CSS star rating |
| HTML | `templates/add_service.html` | Add service |
| HTML | `templates/cancel.html` | Cancel booking |
| HTML | `templates/my_bookings.html` | My bookings |
| HTML | `templates/review.html` | Review |
| Test | `tests/conftest.py` |  |
| Test | `tests/helpers.py` | Small helpers shared by all test files (sign in as customer/admin, book a room, finish a stay, …). |
| Test | `tests/test_p4_after_booking.py` | Person 4 – After booking: my bookings, cancel + refund, add service, review.   Run:  pytest tests/test_p4_after_booking.py -v |

## Liên kết sang file của người khác (không có trong gói này)
- `models/booking.py` – `Payment.refund`, `Booking` (Người 3)
- `services/booking_service.py` – phần lõi (`_owned`, `dto`) mà mixin của bạn dùng (Người 3)
- `templates/room_detail.html` – liên kết sang trang review (Người 2)
- `controllers/helpers.py` (`save_image`), `static/css/base.css` (lớp `.sky`, `.star-on`) (Người 6)

## Cách làm việc
1. Trong dự án đầy đủ: `pip install -r requirements.txt` rồi `python app.py` (http://localhost:5000).
2. Chạy test của bạn: `pytest tests/test_p4_*.py -v`.
3. Review theo luồng: template (HTML) → controller → actor → service → repository (SQL); đối chiếu use case ở `docs/TRACEABILITY.md`.
4. Mỗi lỗi tìm thấy: tạo GitHub Issue, sửa bằng Pull Request, chạy lại test.
5. Viết test case vào **Testing Document Template** của giảng viên (xem `docs/TASK_ASSIGNMENT.md`).
