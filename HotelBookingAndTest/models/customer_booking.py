"""Customer operations: choose a room, create a booking, apply voucher, pay."""
from config import ApiError
from models.room import Room
from models.booking import Voucher

class CustomerBooking:
    """select_room, create_booking, apply_voucher, pay"""
    def select_room(self, room_id, check_in_date, check_out_date):
        r = self.ctx.rooms.get(room_id, 'id')
        if not r: raise ApiError('Not found', 404)
        self._selection = (room_id, check_in_date, check_out_date); return Room.from_row(r).is_available(check_in_date, check_out_date)
    def create_booking(self, number_of_adult, number_of_children, services=(), vouchers=(), notes=''):
        if not self._selection: raise ApiError('Select a room first')
        rid, cin, cout = self._selection
        return self.ctx.book.create(self.user, dict(rid=rid, cin=cin, cout=cout, adults=number_of_adult, kids=number_of_children, svc=list(services), vouchers=list(vouchers), notes=notes))
    def apply_voucher(self, voucher_code):
        v = self.ctx.vouchers.get(voucher_code); return bool(v) and Voucher.from_row(v).is_valid()
    def pay(self, booking_id, payment_method): self.ctx.book.pay(self.user, booking_id, payment_method); return True
