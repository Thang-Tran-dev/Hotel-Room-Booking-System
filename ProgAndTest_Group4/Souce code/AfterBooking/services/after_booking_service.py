"""Booking use cases after booking: cancel (+ refund), add service, review."""
import datetime as dt
from config import ApiError, today
from models.booking import Booking, Payment

class AfterBookingMixin:
    """cancel, review, add_service, reviewable"""
    def cancel(self, u, code):
        b = self._owned(u, code)
        if b['status'] not in ('pending', 'confirmed'): raise ApiError('Cannot cancel in this status')
        refund = bool(b['paid']) and (dt.date.fromisoformat(b['cin']) - today()).days >= 1
        self.bookings.set(code, {'status': 'cancelled', 'paid': 0 if refund else b['paid']})
        pay = self.payments.get(code, 'bcode')
        if refund and pay: Payment.from_row(pay).refund(b['deposit'])                          # «extend» Refund payment
        return b['deposit'] if refund else 0
    def review(self, u, j):
        b = self.db.q("select * from bookings where code=? and uid=? and status='completed'", (j.get('code'), u['id']), True)
        if not b or self.reviews.get(b['id'], 'bid'): raise ApiError('This booking cannot be reviewed')
        if not 1 <= int(j.get('stars') or 0) <= 5 or not (j.get('text') or '').strip(): raise ApiError('Please choose a star rating and write a review')
        self.reviews.add(dict(uid=u['id'], rid=b['rid'], bid=b['id'], stars=j['stars'], text=j['text'], img=j.get('img'), at=today().isoformat()))
    def add_service(self, u, code, scode):
        b = self._owned(u, code)
        if b['status'] not in ('pending', 'confirmed', 'checkedin'): raise ApiError('Cannot add a service in this status')
        if not scode or not self.services.get(scode): raise ApiError('Not found', 404)
        svc = [x for x in (b['svc'] or '').split(',') if x]
        if scode in svc: raise ApiError('Service already added')
        self.bookings.set(code, {'svc': ','.join(svc + [scode])}); Booking.from_row(self.bookings.get(code)).calculate_total(); return True
    def reviewable(self, u, rid):
        b = self.db.q("select code from bookings b where uid=? and rid=? and status='completed' and not exists(select 1 from reviews where bid=b.id)", (u['id'], rid), True)
        if not b: raise ApiError('This booking cannot be reviewed')
        return b['code']
