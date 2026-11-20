"""Booking use cases: create a booking, pay, view."""
import datetime as dt
import random
from config import ApiError, Config, now, today
from models.booking import Booking, Payment, Invoice

from services.after_booking_service import AfterBookingMixin
from services.admin_booking_service import AdminBookingMixin

class BookingService(AfterBookingMixin, AdminBookingMixin):
    """Booking life-cycle: create + pay live here; the rest is in the two mixins above (one file per owner)."""
    def __init__(self, db, bookings, rooms, users, services, reviews, pricing, mailer, details, payments, invoices):
        self.db, self.bookings, self.rooms, self.users, self.services, self.reviews, self.pricing, self.mail = db, bookings, rooms, users, services, reviews, pricing, mailer
        self.details, self.payments, self.invoices = details, payments, invoices
    def dto(self, b):
        d = dict(b); r = self.rooms.get(b['rid'], 'id')
        d.update(room=r['code'], type=r['type'], img=r['img'], cust=self.users.get(b['uid'])['name'],
                 services=[s['name'] for s in self.services.all() if s['code'] in (b['svc'] or '').split(',')], reviewed=bool(self.reviews.get(b['id'], 'bid')), summary=Booking.from_row(b).get_payment_summary()); return d
    def _owned(self, u, code):
        b = self.bookings.get(code)
        if not b or (b['uid'] != u['id'] and u['role'] != 'admin'): raise ApiError('Not found', 404)
        return b
    def mine(self, u): return [self.dto(b) for b in self.bookings.of_user(u['id'])]
    def one(self, u, code): return self.dto(self._owned(u, code))
    def new_code(self, cin): return 'DHH-%s-%04d' % (cin[:4], random.randint(0, 9999))
    def create(self, u, j):
        try: r = self.rooms.get(j['rid'], 'id'); cin = dt.date.fromisoformat(j['cin'])
        except (KeyError, TypeError, ValueError): raise ApiError('Invalid booking details')
        if not r: raise ApiError('Not found', 404)
        if cin < today(): raise ApiError('Check-in cannot be before today')
        adults, kids = j.get('adults', 0), j.get('kids', 0)
        if adults + kids > r['cap'] or adults < 1: raise ApiError('Guests exceed capacity (at least 1 adult required)')
        p = self.pricing.quote(j['rid'], j['cin'], j['cout'], j.get('svc', []), j.get('vouchers', []))
        self.db.begin()                                                                # lock → no double booking
        if self.bookings.busy(j['rid'], j['cin'], j['cout']): self.db.rollback(); raise ApiError('This room is already booked for these dates', 409)
        code = self.new_code(j['cin']); hold = (dt.datetime.now() + dt.timedelta(minutes=Config.HOLD_MIN)).isoformat()
        self.bookings.add(dict(code=code, uid=u['id'], rid=j['rid'], cin=j['cin'], cout=j['cout'], adults=adults, kids=kids, svc=','.join(j.get('svc', [])), voucher=','.join(j.get('vouchers', [])), total=p['total'], deposit=p['deposit'], vat=p['vat'], discount=p['discount'], hold=hold, created=now(), notes=j.get('notes', '')), commit=False)
        self.details.add(dict(detail_id='D-' + code, bcode=code, rid=j['rid'], nights=p['nights'], room_price=r['price'], sub_total=p['room']), commit=False)
        self.db.commit(); return dict(code=code, hold=hold, **p)
    def pay(self, u, code, method):
        b = self.bookings.get(code)
        if not b or b['uid'] != u['id'] or b['status'] != 'pending': raise ApiError('Invalid booking')
        if b['hold'] and b['hold'] < now() and not b['paid']: self.bookings.set(code, {'status': 'cancelled'}); raise ApiError('Room hold expired (15 minutes)', 410)
        if method not in ('momo', 'bank', 'card', 'hotel'): raise ApiError('Choose a payment method')
        Payment.new(code, b['deposit'] if method != 'hotel' else 0, method).process()          # Make payment
        self.bookings.set(code, {'paid': 0 if method == 'hotel' else 1, 'method': method, 'hold': None})
        Invoice.new(code, b['total']).issue_invoice().send_email(u['email'])                  # «include» Issue invoice
