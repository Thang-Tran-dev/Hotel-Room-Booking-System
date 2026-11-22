"""Person 3 – Booking and payment: book room, voucher, extra service price, pay, invoice.   Run:  pytest tests/test_p3_booking.py -v"""
import pytest
from config import ApiError
from helpers import d, customer, book, row, login

def test_book_room_success(h): assert 'code' in book(customer(h))
def test_book_room_in_the_past(h):
    with pytest.raises(ApiError, match='before today'): book(customer(h), a=-1, b=1)
def test_book_room_over_capacity(h):
    with pytest.raises(ApiError, match='capacity'): book(customer(h), rid=2, adults=5)
def test_book_room_no_double_booking(h):
    c = customer(h); book(c)
    with pytest.raises(ApiError) as e: book(c, a=11, b=13)
    assert e.value.code == 409
def test_apply_voucher(h): c = customer(h); assert c.apply_voucher('WELCOME10') is True and c.apply_voucher('NOPE') is False
def test_book_with_voucher_discount(h): assert book(customer(h), vouchers=['WELCOME10'])['discount'] > 0
def test_book_with_invalid_voucher(h):
    with pytest.raises(ApiError, match='invalid'): book(customer(h), vouchers=['NOPE'])
def test_book_with_extra_service_costs_more(h): assert h.pricing.quote(1, d(10), d(12), ['S120'], [])['total'] > h.pricing.quote(1, d(10), d(12), [], [])['total']
def test_pay_online_creates_payment_and_invoice(h):
    c = customer(h); code = book(c)['code']; assert c.pay(code, 'momo') is True
    assert row(h.payments, code, 'bcode')['status'] == 'paid' and row(h.invoices, 'INV-' + code)
def test_pay_invalid_method(h):
    c = customer(h); code = book(c)['code']
    with pytest.raises(ApiError): c.pay(code, 'x')
def test_pay_at_hotel_is_pending(h): c = customer(h); code = book(c)['code']; c.pay(code, 'hotel'); assert row(h.payments, code, 'bcode')['status'] == 'pending'
def test_full_booking_flow_with_forms(client):
    login(client); client.post('/book/302-DLX', data={'cin': d(10), 'cout': d(12), 'adults': 1, 'kids': 0, 'service': 'S120'})
    assert client.get('/booking').status_code == 200
    client.post('/booking/voucher', data={'voucher': 'WELCOME10'})
    r = client.post('/booking/confirm', data={'name': 'Andrew', 'email': 'andrew@gmail.com', 'phone': '0911111111', 'pm': 'momo'}); pay_url = r.headers['Location']; assert '/pay/' in pay_url
    page = client.get(pay_url); assert b'Momo / Bank payment' in page.data and b'Credit / Debit card' in page.data
    assert client.post(pay_url, data={'method': 'momo'}).headers['Location'].startswith('/success/')
    assert b'PENDING' in client.get('/my').data
    code = pay_url.rsplit('/', 1)[1]; assert client.get(f'/my/{code}/cancel').status_code == 200
    client.post(f'/my/{code}/cancel', data={'accept': 'on'}); assert b'CANCELLED' in client.get('/my').data
def test_card_payment_needs_valid_details(client):
    login(client); client.post('/book/302-DLX', data={'cin': d(10), 'cout': d(12), 'adults': 1, 'kids': 0}); code = client.post('/booking/confirm', data={'name': 'A', 'email': 'a@b.com', 'phone': '0911111111', 'pm': 'card'}).headers['Location']
    r = client.post(code, data={'method': 'card', 'holder': ''}, headers={'Referer': code}, follow_redirects=True); assert b'valid payment details' in r.data
