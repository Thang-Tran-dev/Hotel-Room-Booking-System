# Người 3 – Đặt phòng, giá, thanh toán, hóa đơn

**Use case của bạn:** Book room, Apply voucher, Make payment, Pay online, Pay at hotel, Issue invoice

Gói này chỉ chứa **các file bạn phải review** (đã xóa mọi file không liên quan). Để chạy được chương trình hãy dùng dự án đầy đủ `hotel.zip`, rồi mở các file dưới đây trong đó.

## File của bạn
| Loại | File | Nội dung |
|---|---|---|
| Python | `controllers/booking.py` | Book a room: room page → booking summary (+ voucher) → confirm → payment → success. |
| Python | `models/actors/customer_booking.py` | Customer operations: choose a room, create a booking, apply voucher, pay. |
| Python | `models/booking.py` | Booking, BookingDetail, Payment, Invoice, Voucher entities + their repositories. |
| Môi trường | `models/database.py` | Database connection, table creation / migration, sample data, and the (simulated) e-mail sender. |
| Python | `services/booking_service.py` | Booking use cases: create a booking, pay, view. |
| Python | `services/pricing_service.py` | Price calculation: nights × price + services − vouchers + VAT, deposit 30 %. |
| CSS | `static/css/booking.css` | BOOKING: booking summary, price lines, voucher, payment (QR / card), success |
| HTML | `templates/_macros.html` | Room summary card shown on the booking and payment pages |
| HTML | `templates/booking.html` | Booking |
| HTML | `templates/payment.html` | Payment |
| HTML | `templates/success.html` | Payment successful |
| Test | `tests/conftest.py` |  |
| Test | `tests/helpers.py` | Small helpers shared by all test files (sign in as customer/admin, book a room, finish a stay, …). |
| Test | `tests/test_p3_booking.py` | Person 3 – Booking and payment: book room, voucher, extra service price, pay, invoice.   Run:  pytest tests/test_p3_booking.py -v |

## Liên kết sang file của người khác (không có trong gói này)
- `templates/room_detail.html` – form "Book now" (Người 2)
- `services/after_booking_service.py` – `BookingService` kế thừa mixin của Người 4; `services/admin_booking_service.py` – mixin của Người 5
- `models/mailer.py` – gửi hóa đơn (Người 4)
- `templates/my_bookings.html` – nút Pay dẫn tới `customer.pay` (Người 4)
- `models/base.py`, `controllers/helpers.py` (`qr_svg`), `templates/base.html` (Người 6)

## Cách làm việc
1. Trong dự án đầy đủ: `pip install -r requirements.txt` rồi `python app.py` (http://localhost:5000).
2. Chạy test của bạn: `pytest tests/test_p3_*.py -v`.
3. Review theo luồng: template (HTML) → controller → actor → service → repository (SQL); đối chiếu use case ở `docs/TRACEABILITY.md`.
4. Mỗi lỗi tìm thấy: tạo GitHub Issue, sửa bằng Pull Request, chạy lại test.
5. Viết test case vào **Testing Document Template** của giảng viên (xem `docs/TASK_ASSIGNMENT.md`).
