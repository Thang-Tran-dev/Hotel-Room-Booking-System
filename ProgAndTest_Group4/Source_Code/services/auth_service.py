"""Use cases: register, sign in, reset / change password, profile."""
import random, string
from flask import session
from werkzeug.security import generate_password_hash as H, check_password_hash as C
from config import Config, ApiError

class AuthService:
    def __init__(self, users, mailer): self.users, self.mail = users, mailer
    def current(self): return self.users.get(session['u']) if 'u' in session else None
    def require(self, admin=False):
        u = self.current()
        if not u: raise ApiError('Please sign in', 401)
        if admin and u['role'] != 'admin': raise ApiError('Permission denied', 403)
        return u
    def register(self, j):
        n, e, p, pw = [(j.get(k) or '').strip() for k in ('name', 'email', 'phone', 'pw')]
        if not n: raise ApiError('Full name is required')
        if not Config.EMAIL.match(e): raise ApiError('Invalid email address')
        if not Config.PHONE.match(p): raise ApiError('Invalid phone number')
        if not Config.PW.match(pw): raise ApiError('Password must be at least 8 characters with uppercase, lowercase, a digit and a special character')
        if pw != j.get('pw2'): raise ApiError('Passwords do not match')
        if self.users.by_email(e): raise ApiError('Email is already registered')
        self.users.add(dict(name=n, email=e, phone=p, pw=H(pw)))
    def login(self, j):
        u = self.users.by_email((j.get('email') or '').strip())
        if not u: raise ApiError('Wrong email or password')
        if u['locked']: raise ApiError('This account is locked', 403)
        if not C(u['pw'], j.get('pw') or ''):
            f = u['fails'] + 1; self.users.set(u['id'], {'fails': f})
            if f > 3:
                self.mail.send(u['email'], 'Login warning', 'Your account had more than 3 failed login attempts.')
                self.mail.send('admin@hotel.com', 'Warning', u['email'] + ' had more than 3 failed login attempts')
            raise ApiError(f'Wrong email or password (attempt {f})')
        self.users.set(u['id'], {'fails': 0}); session['u'] = u['id']; session.permanent = bool(j.get('remember')); return u
    def forgot(self, e):
        u = self.users.by_email((e or '').strip())
        if not u: raise ApiError('Email does not exist')
        p = 'Aa1!' + ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        self.users.set(u['id'], {'pw': H(p)}); self.mail.send(u['email'], 'Your new password', p)
    def change_password(self, u, j):
        if not C(u['pw'], j.get('old') or ''): raise ApiError('Old password is incorrect')
        n = j.get('new') or ''
        if not Config.PW.match(n) or n == j['old']: raise ApiError('New password is invalid or the same as the old one')
        if n != j.get('new2'): raise ApiError('Confirmation does not match')
        self.users.set(u['id'], {'pw': H(n)}); self.mail.send(u['email'], 'Password changed', 'Your password was just changed')
    def update_profile(self, u, j):
        if not j.get('name') or not Config.PHONE.match(j.get('phone') or ''): raise ApiError('Invalid name or phone number')
        self.users.set(u['id'], {k: j.get(k) for k in ('name', 'phone', 'idcard', 'address', 'dob', 'sex')}); return self.users.get(u['id'])
