# Hotel Booking – HTML + CSS + Python only (Flask + SQLite)

## Run
```
pip install -r requirements.txt
python app.py            # open http://localhost:5000
```
Admin: `admin@hotel.com` – password = `Admin@123` · Customer demo: `andrew@gmail.com` / `Andrew@123`
Tests: `pip install pytest && pytest -v`  (one person only: `pytest tests/test_p3_booking.py -v`)   ·   E-mails are written to `emails.log` (simulated).

```
hotel/
├── app.py                      START HERE – builds the app, connects everything
├── config.py                   settings (VAT, deposit %, password rules, ApiError)
│
├── templates/                  VIEW  (HTML, Jinja)
│   ├── base.html               navbar + frame of every page
│   ├── auth/  profile.html  password.html             ← Person 1
│   ├── home.html  rooms.html  room_detail.html        ← Person 2
│   ├── booking.html  payment.html  success.html       ← Person 3
│   ├── my_bookings.html  cancel.html  add_service.html  review.html   ← Person 4
│   └── admin/  (_layout, bookings, revenue, users, user_new ← 5 · rooms, vouchers, services ← 6)
├── static/css/                 CSS: base · auth · rooms · booking · after_booking · admin
├── static/images/              photos           static/uploads/  pictures uploaded by users
│
├── controllers/                CONTROLLER – one function per page (form → model → template)
│   ├── blueprints.py  helpers.py                      shared (Person 6)
│   ├── auth.py  account.py                            Person 1
│   ├── rooms.py                                       Person 2
│   ├── booking.py                                     Person 3
│   ├── my_bookings.py                                 Person 4
│   ├── admin_operations.py                            Person 5
│   └── admin_catalog.py                               Person 6
├── services/                   business rules: auth_service · room_service · pricing_service · booking_service
│                               · after_booking_service (4) · admin_booking_service (5)
├── models/                     MODEL – class-diagram classes + SQL
│   ├── base.py                 Entity, Repository
│   ├── account.py  room.py  booking.py  review.py     entities + repositories of each area
│   ├── database.py  mailer.py  tables / sample data / e-mail
│   └── actors/                 Guest, Customer, Admin (assembled from small files)
├── tests/                      test_p1_… to test_p6_… : one file per person
```
How one click flows:  **template (form)** → **controller** → **actor method** (`Customer.pay`) → **service** → **repository (SQL)** → back to a **template**.

