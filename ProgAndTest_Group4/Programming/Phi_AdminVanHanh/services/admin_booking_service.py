"""Admin use cases on bookings: approve / reject, check-in, check-out, charges, revenue, create customer."""
import datetime as dt
from werkzeug.security import generate_password_hash as H
from config import ApiError, Config, num, now, today
from models.booking import Booking, Payment, Invoice

class AdminBookingMixin:
    """create_for_guest, admin_action, revenue, create_customer"""
    def create_for_guest(self, uid, j, p):
        code = self.new_code(j['cin']); self.bookings.add(dict(code=code, uid=uid, rid=j['rid'], cin=j['cin'], cout=j['cout'], adults=j.get('adults', 1), kids=j.get('kids', 0), total=p['total'], deposit=p['deposit'], status='confirmed', method='hotel', vat=p['vat'], discount=p['discount'], created=now(), notes='Booked at the front desk - pay at hotel'))
        self.details.add(dict(detail_id='D-' + code, bcode=code, rid=j['rid'], nights=p['nights'], room_price=p['room'] / p['nights'], sub_total=p['room']))
        Payment.new(code, 0, 'hotel').process()
    def admin_action(self, code, act, j):
        b = self.bookings.get(code)
        if not b: raise ApiError('Not found', 404)
        S = b['status']; ok = lambda s: S == s
        if act == 'approve' and ok('pending'): self._to(b, 'confirmed', hold=None)
        elif act == 'reject' and ok('pending'): self._to(b, 'cancelled')
        elif act == 'checkin' and ok('confirmed'):
            cu = self.users.get(b['uid']); idc = (j.get('idcard') or '').strip()
            if not idc: raise ApiError('Enter the ID card number to verify')
            if cu['idcard'] and cu['idcard'] != idc: raise ApiError('ID card does not match the booking')
            self.users.set(cu['id'], {'idcard': idc}); self._to(b, 'checkedin')
        elif act == 'charge' and ok('checkedin'):
            a = num(j.get('amount') if j.get('amount') not in (None, '') else -1)
            if a < 0 or not j.get('reason'): raise ApiError('Amount must be ≥ 0 and a reason is required')
            self.bookings.set(code, {'extra': b['extra'] + a, 'total': b['total'] + a, 'notes': b['notes'] + f" | +${a}: {j['reason']}"})
        elif act == 'checkout' and ok('checkedin'):
            self._to(b, 'completed', paid=1)
            Invoice.new(code, b['total']).issue_invoice().send_email(self.users.get(b['uid'])['email'])
        else: raise ApiError('Action not allowed in the current status')
    def _to(self, b, status, **extra):
        Booking.from_row(b).update_status(status)
        if extra: self.bookings.set(b['code'], extra)
    def revenue(self):
        rows = [self.dto(b) for b in self.bookings.newest(True)]
        return dict(rows=rows, total=sum(b['total'] for b in rows if b['status'] == 'completed'), deposits=sum(b['deposit'] for b in rows if b['paid']))
    def create_customer(self, j):
        if not j.get('name') or not j.get('phone') or not j.get('idcard') or not Config.PW.match(j.get('pw') or ''): raise ApiError('Missing information or invalid temporary password')
        em = j.get('email') or j['phone'] + '@walkin.local'
        if self.users.by_email(em): raise ApiError('Account already exists')
        p = None
        if j.get('rid'):
            r = self.rooms.get(j['rid'], 'id')
            try:
                if dt.date.fromisoformat(j.get('cin') or '') < today(): raise ApiError('Check-in cannot be before today')
            except ValueError: raise ApiError('Invalid date range')
            if not r or j.get('adults', 1) + j.get('kids', 0) > r['cap']: raise ApiError('Room not found or guests exceed capacity')
            p = self.pricing.quote(j['rid'], j['cin'], j['cout'], [], [])
            if self.bookings.busy(j['rid'], j['cin'], j['cout']): raise ApiError('This room is already booked for these dates', 409)
        self.users.add({'name': j['name'], 'email': em, 'phone': j['phone'], 'pw': H(j['pw']), 'idcard': j['idcard'], 'address': j.get('address'), 'dob': j.get('dob'), 'sex': j.get('sex')})
        self.mail.send(em, 'New account', 'Temporary password: ' + j['pw'])
        if p: self.create_for_guest(self.users.by_email(em)['id'], j, p)
