"""Person 4 – After booking: my bookings, cancel + refund, add service, review.   Run:  pytest tests/test_p4_after_booking.py -v"""
import pytest
from config import ApiError
from models.actors import Guest
from helpers import customer, book, row, finished_stay

def test_view_my_bookings(h): c = customer(h); book(c); assert len(c.view_booking_history()) == 1
def test_cancel_paid_booking_refunds_payment(h):
    c = customer(h); code = book(c)['code']; c.pay(code, 'card'); assert c.cancel_booking(code) and c.last_refund > 0 and row(h.payments, code, 'bcode')['status'] == 'refunded'
def test_cancel_unpaid_booking_no_refund(h): c = customer(h); code = book(c)['code']; c.cancel_booking(code); assert c.last_refund == 0
def test_cancel_other_users_booking(h):
    code = book(customer(h))['code']; Guest(h).sign_up('B', 'Bb@123456', 'b@b.com', '0912345678')
    with pytest.raises(ApiError) as e: customer(h, 'b@b.com', 'Bb@123456').cancel_booking(code)
    assert e.value.code == 404
def test_add_service_increases_total(h):
    c = customer(h); code = book(c)['code']; before = h.book.one(c.user, code)['total']
    assert c.add_service(code, 'S005') is True and h.book.one(c.user, code)['total'] > before
def test_add_service_twice_rejected(h):
    c = customer(h); code = book(c)['code']; c.add_service(code, 'S005')
    with pytest.raises(ApiError): c.add_service(code, 'S005')
def test_review_before_checkout_rejected(h):
    c = customer(h); code = book(c)['code']
    with pytest.raises(ApiError): c.write_review(1, 5, 'x', booking_code=code)
def test_review_after_stay(h): c, a, code = finished_stay(h); assert c.write_review(1, 5, 'Great', booking_code=code) and Guest(h).view_room_detail('302-DLX')['reviews'] == 1
def test_review_twice_rejected(h):
    c, a, code = finished_stay(h); c.write_review(1, 5, 'a', booking_code=code)
    with pytest.raises(ApiError): c.write_review(1, 4, 'b', booking_code=code)
