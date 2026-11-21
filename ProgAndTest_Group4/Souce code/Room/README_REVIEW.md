# Trang chủ, danh sách & chi tiết phòng

**Use case trong phần này:** View room list, View room detail, Search room, Filter room

Gói này chỉ chứa **các file liên quan đến hiển thị và làm việc với phòng**. Để chạy được chương trình hãy dùng dự án đầy đủ `hotel.zip`, rồi mở các file dưới đây trong đó.

## File bao gồm
| Loại | File | Nội dung |
|---|---|---|
| Python | `controllers/rooms.py` | Home page, room list and room detail. |
| Python | `models/actors/guest_rooms.py` | Guest operations about rooms: list, detail, search, filter. |
| Python | `models/room.py` | Room, RoomType, Service entities + their repositories. |
| Môi trường | `requirements.txt` | thư viện cần cài |
| Python | `services/room_service.py` | Room list, search / filter and room detail. |
| CSS | `static/css/rooms.css` | ROOMS: home page, room list, room detail |
| HTML | `templates/home.html` |  |
| HTML | `templates/room_detail.html` | {{ room.code }} |
| HTML | `templates/rooms.html` | Rooms |
| Test | `tests/conftest.py` |  |
| Test | `tests/helpers.py` | Small helpers shared by all test files (sign in as customer/admin, book a room, finish a stay, …). |
| Test | `tests/test_p2_rooms.py` | Person 2 – Rooms: list, detail, search, filter.   Run:  pytest tests/test_p2_rooms.py -v |

## Liên kết sang file của người khác (không có trong gói này)
- `models/booking.py` – `BookingRepo.busy()` quyết định phòng còn trống (Người 3)
- `controllers/booking.py` – nút "Book now" gửi form tới `customer.start_booking` (Người 3)
- `controllers/my_bookings.py` – nút "Review this room" tới `customer.review` (Người 4)
- `templates/base.html`, `static/css/base.css` (Người 6)

## Cách làm việc
1. Trong dự án đầy đủ: `pip install -r requirements.txt` rồi `python app.py` (http://localhost:5000).
2. Chạy test của bạn: `pytest tests/test_p2_*.py -v`.
3. Review theo luồng: template (HTML) → controller → actor → service → repository (SQL); đối chiếu use case ở `docs/TRACEABILITY.md`.
4. Mỗi lỗi tìm thấy: tạo GitHub Issue, sửa bằng Pull Request, chạy lại test.
5. Viết test case vào **Testing Document Template** của giảng viên (xem `docs/TASK_ASSIGNMENT.md`).
