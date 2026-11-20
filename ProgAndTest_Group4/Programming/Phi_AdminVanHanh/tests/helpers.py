"""Small helpers shared by all test files (sign in as customer/admin, book a room, finish a stay, …)."""
import datetime as dt
from models.actors import Guest

def d(n): return (dt.date.today() + dt.timedelta(n)).isoformat()
def customer(h, email='andrew@gmail.com', pw='Andrew@123'): return Guest(h).sign_in(email, pw)
def admin(h): return Guest(h).sign_in('admin@hotel.com', 'Admin@123')
def book(c, rid=1, a=10, b=12, adults=1, kids=0, services=(), vouchers=()): c.select_room(rid, d(a), d(b)); return c.create_booking(adults, kids, services, vouchers)
def row(repo, key, col=None): r = repo.get(key, col); return dict(r) if r else None
def finished_stay(h):
    c = customer(h); code = book(c)['code']; c.pay(code, 'card'); a = admin(h)
    a.approve_booking(code); a.check_in(code, '063918304722'); a.check_out(code); return c, a, code
def login(c, email='andrew@gmail.com', pw='Andrew@123'): return c.post('/login', data={'email': email, 'pw': pw})

PUBLIC = ['/', '/rooms', '/rooms?q=DLX&min=0&max=0', '/rooms/302-DLX', '/login', '/signup', '/forgot']
ADMIN = ['/admin/bookings', '/admin/revenue', '/admin/users', '/admin/users/new', '/admin/rooms', '/admin/rooms?edit=302-DLX', '/admin/vouchers', '/admin/services']
