"""Person 5 – Admin operations: approve, check-in / out, charges, revenue, users.   Run:  pytest tests/test_p5_admin_ops.py -v"""
import pytest
from config import ApiError
from helpers import d, customer, admin, book, row, finished_stay, login, ADMIN

def test_admin_approve_booking(h): code = book(customer(h))['code']; assert admin(h).approve_booking(code) and row(h.bookings, code)['status'] == 'confirmed'
def test_admin_checkin_wrong_id_card(h):
    code = book(customer(h))['code']; a = admin(h); a.approve_booking(code)
    with pytest.raises(ApiError, match='does not match'): a.check_in(code, '000')
def test_admin_checkout_issues_invoice(h): c, a, code = finished_stay(h); assert row(h.invoices, 'INV-' + code)['total_amount'] > 0 and row(h.bookings, code)['status'] == 'completed'
def test_admin_charge_requires_checkin(h):
    code = book(customer(h))['code']
    with pytest.raises(ApiError): admin(h).add_incidental_charge(code, 5, 'x')
def test_admin_incidental_charge_adds_to_total(h):
    code = book(customer(h))['code']; a = admin(h); a.approve_booking(code); a.check_in(code, '063918304722'); t = row(h.bookings, code)['total']
    a.add_incidental_charge(code, 15, 'minibar'); assert row(h.bookings, code)['total'] == t + 15
def test_admin_view_revenue(h): finished_stay(h); assert admin(h).view_revenue()['total'] > 0
def test_customer_cannot_open_admin_pages(h):
    customer(h)
    with pytest.raises(ApiError) as e: h.auth.require(admin=True)
    assert e.value.code == 403
def test_admin_create_customer_with_booking(h):
    a = admin(h); a.manage_user('create', data={'name': 'Khach', 'phone': '0933333333', 'idcard': '0123', 'pw': 'Temp@1234', 'rid': 2, 'cin': d(40), 'cout': d(42), 'adults': 2, 'kids': 0})
    assert any(b['cust'] == 'Khach' and b['method'] == 'hotel' for b in a.view_all_bookings())
def test_admin_lock_and_unlock_user(h):
    a = admin(h); a.manage_user('lock', user_id=2); assert a.manage_user('list')[0]['locked'] == 1; a.manage_user('lock', user_id=2); assert a.manage_user('list')[0]['locked'] == 0
def test_customer_is_kept_out_of_admin_pages(client): login(client); r = client.get('/admin/bookings'); assert r.status_code == 302 and r.headers['Location'].endswith('/')
def test_admin_pages_open_for_admin(client): login(client, 'admin@hotel.com', 'Admin@123'); assert all(client.get(u).status_code == 200 for u in ADMIN)
