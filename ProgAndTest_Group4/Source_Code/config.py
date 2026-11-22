"""Settings, helpers and the shared ApiError."""
import os, re, random, string, datetime as dt

BASE = os.path.dirname(os.path.abspath(__file__))
def num(x):
    try: return float(x or 0)
    except (TypeError, ValueError): return 0.0
def now(): return dt.datetime.now().isoformat()
def today(): return dt.date.today()

# ───────────── Config & errors ─────────────
class Config:
    DB = os.path.join(BASE, 'hotel.db'); VAT = .05; DEPOSIT = .3; HOLD_MIN = 15; PAGE = 3; REVIEW_IMAGES = 5
    PW = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,}$')
    PHONE = re.compile(r'^\+?\d{9,12}$'); EMAIL = re.compile(r'^[^@\s]+@[^@\s]+\.\w+$')
    ADMIN_PW = os.environ.get('ADMIN_PASSWORD', 'Admin@123'); IMAGES = ('.png', '.jpg', '.jpeg', '.gif', '.webp')
    @staticmethod
    def secret():
        f = os.path.join(BASE, 'secret.key')
        if not os.path.exists(f): open(f, 'w').write(''.join(random.choices(string.ascii_letters + string.digits, k=48)))
        return os.environ.get('SECRET') or open(f).read()

class ApiError(Exception):
    def __init__(self, msg, code=400): super().__init__(msg); self.msg, self.code = msg, code
