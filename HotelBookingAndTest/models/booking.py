"""Booking, BookingDetail, Payment, Invoice, Voucher entities + their repositories."""
from config import ApiError, num, now, today
from models.base import Entity, Repository

class BookingDetail(Entity): FIELDS = {'detail_id': 'detail_id', 'number_of_night': 'nights', 'room_price': 'room_price', 'sub_total': 'sub_total'}

class Voucher(Entity):
    FIELDS = {'voucher_code': 'code', 'discount_percent': 'pct', 'start_date': 'start', 'expiry_date': 'end', 'is_active': 'active', 'condition': 'cond'}
    def is_valid(self, day=None):
        day = day or today().isoformat(); return bool(self.is_active and self.start_date <= day <= self.expiry_date)

class Booking(Entity):
    FIELDS = {'booking_id': 'code', 'status': 'status', 'check_in_date': 'cin', 'check_out_date': 'cout', 'number_of_adult': 'adults', 'number_of_children': 'kids', 'deposit': 'deposit', 'vat': 'vat', 'discount': 'discount', 'total_price': 'total'}
    def calculate_total(self):
        r = self.row; p = self.ctx.pricing.quote(r['rid'], r['cin'], r['cout'], [x for x in (r['svc'] or '').split(',') if x], [x for x in (r['voucher'] or '').split(',') if x], r['extra'])
        self.total_price, self.vat, self.discount = p['total'], p['vat'], p['discount']
        self.ctx.bookings.set(self.booking_id, {'total': p['total'], 'vat': p['vat'], 'discount': p['discount']}); return p['total']
    def get_payment_summary(self):
        tot, dep = self.total_price or 0, self.deposit or 0
        return {'total': tot, 'vat': self.vat or 0, 'discount': self.discount or 0, 'deposit': dep, 'remaining': round(tot - dep, 2)}
    def update_status(self, status): self.ctx.bookings.set(self.booking_id, {'status': status}); self.status = status

class Payment(Entity):
    FIELDS = {'payment_id': 'payment_id', 'bcode': 'bcode', 'amount': 'amount', 'payment_method': 'method', 'payment_date': 'paid_at', 'status': 'status', 'refund_amount': 'refund_amount'}
    @classmethod
    def new(cls, bcode, amount, method): return cls(payment_id='P-' + bcode, bcode=bcode, amount=amount, payment_method=method, status='pending', refund_amount=0, payment_date=now())
    def _save(self): self.ctx.payments.save(dict(payment_id=self.payment_id, bcode=self.bcode, amount=self.amount, method=self.payment_method, paid_at=self.payment_date, status=self.status, refund_amount=self.refund_amount))
    def process(self):
        self.status = 'pending' if self.payment_method == 'hotel' else 'paid'; self.payment_date = now(); self._save(); return True
    def refund(self, amount):
        if not 0 < amount <= (self.amount or 0): return False
        self.refund_amount, self.status = amount, 'refunded'; self._save(); return True

class Invoice(Entity):
    FIELDS = {'invoice_id': 'invoice_id', 'bcode': 'bcode', 'issue_date': 'issued', 'total_amount': 'total_amount'}
    @classmethod
    def new(cls, bcode, total): return cls(invoice_id='INV-' + bcode, bcode=bcode, total_amount=total, issue_date=today().isoformat())
    def issue_invoice(self):
        self.ctx.invoices.save(dict(invoice_id=self.invoice_id, bcode=self.bcode, issued=self.issue_date, total_amount=self.total_amount)); return self
    def send_email(self, email): self.ctx.mail.send(email, 'Invoice ' + self.bcode, f'Invoice {self.invoice_id}: total ${self.total_amount}'); return True

class VoucherRepo(Repository):
    table, key, cols = 'vouchers', 'code', ('code', 'pct', 'start', 'end', 'cond')
    def validate(self, d):
        super().validate(d)
        if not (1 <= num(d.get('pct')) <= 100 and (d.get('end') or '') > (d.get('start') or '')): raise ApiError('Percent must be 1–100 and the expiry date must be after the start date')
    def remove(self, v): self.db.q('update vouchers set active=1-active where code=?', (v,))   # "Disable/Enable"
    def is_valid(self, v, day): return bool(v and v['active'] and v['start'] <= day <= v['end'])

class BookingRepo(Repository):
    table, key = 'bookings', 'code'
    def busy(self, rid, a, b, ex=0):
        """True if the room has a confirmed / checked-in / live-held booking overlapping [a,b)."""
        return self.db.q("select 1 from bookings where rid=? and id!=? and cin<? and cout>? and (status in('confirmed','checkedin') or (status='pending' and (paid=1 or hold is null or hold>?)))", (rid, ex, b, a, now()), True, commit=False) is not None
    def of_user(self, uid): return self.db.q('select * from bookings where uid=? order by id desc', (uid,))
    def newest(self, completed_only=False): return self.db.q("select * from bookings " + ("where status!='cancelled' " if completed_only else '') + 'order by id desc')

class BookingDetailRepo(Repository): table, key = 'booking_details', 'detail_id'

class PaymentRepo(Repository): table, key = 'payments', 'payment_id'

class InvoiceRepo(Repository): table, key = 'invoices', 'invoice_id'
