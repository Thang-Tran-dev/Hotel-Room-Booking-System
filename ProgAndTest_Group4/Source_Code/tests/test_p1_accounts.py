"""Person 1 – Accounts: register, login, logout, reset / change password, profile.   Run:  pytest tests/test_p1_accounts.py -v"""
import pytest
from config import ApiError
from models.actors import Guest
from models.account import Account
from helpers import customer, admin, login

def test_register_success(h): assert Guest(h).sign_up('Lan', 'Lan@12345', 'lan@b.com', '0912345678') is True
def test_register_weak_password(h):
    with pytest.raises(ApiError, match='Password must'): Guest(h).sign_up('Lan', 'abc', 'lan@b.com', '0912345678')
def test_register_password_mismatch(h):
    with pytest.raises(ApiError, match='do not match'): Guest(h).sign_up('Lan', 'Lan@12345', 'lan@b.com', '0912345678', confirm='Lan@1234x')
def test_register_duplicate_email(h):
    with pytest.raises(ApiError, match='already registered'): Guest(h).sign_up('A', 'Lan@12345', 'andrew@gmail.com', '0912345678')
def test_login_success(h): assert customer(h).account.full_name == 'Andrew'
def test_login_returns_admin_actor(h): assert admin(h).admin_id == 1
def test_login_wrong_password(h):
    with pytest.raises(ApiError, match='Wrong email or password'): customer(h, pw='x')
def test_login_unknown_email(h):
    with pytest.raises(ApiError): customer(h, email='no@x.com')
def test_login_locked_account(h):
    admin(h).manage_user('lock', user_id=2)
    with pytest.raises(ApiError, match='locked'): customer(h)
def test_logout(h): c = customer(h); c.account.logout(); assert h.auth.current() is None
def test_reset_password_unknown_email(h):
    with pytest.raises(ApiError): Account().reset_password('no@x.com')
def test_reset_password_success(h):
    assert Account().reset_password('andrew@gmail.com') is True
    with pytest.raises(ApiError): customer(h)
def test_change_password_success(h): assert customer(h).account.change_password('Andrew@123', 'New@12345') is True
def test_change_password_wrong_old(h):
    with pytest.raises(ApiError, match='Old password'): customer(h).account.change_password('bad', 'New@12345')
def test_change_password_weak_new(h):
    with pytest.raises(ApiError): customer(h).account.change_password('Andrew@123', 'weak')
def test_update_profile(h): assert customer(h).update_profile('Andrew N', '0911111111', '063918304722', 'Da Nang', 'Male', '1999-01-02')['dob'] == '1999-01-02'
def test_update_profile_invalid_phone(h):
    with pytest.raises(ApiError): customer(h).update_profile('A', '12', '', '', '', '')
def test_private_pages_redirect_to_login(client):
    for u in ('/my', '/profile', '/password', '/booking', '/admin/bookings'): r = client.get(u); assert r.status_code == 302 and '/login' in r.headers['Location']
def test_wrong_login_shows_error_message(client):
    r = client.post('/login', data={'email': 'andrew@gmail.com', 'pw': 'bad'}, headers={'Referer': '/login'}, follow_redirects=True); assert b'Wrong email or password' in r.data
def test_signup_then_login(client):
    client.post('/signup', data={'name': 'Lan', 'email': 'lan@b.com', 'phone': '0912345678', 'pw': 'Lan@12345', 'pw2': 'Lan@12345'}); assert login(client, 'lan@b.com', 'Lan@12345').status_code == 302
