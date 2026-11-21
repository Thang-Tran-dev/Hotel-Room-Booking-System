"""Admin operations: bookings, check-in / check-out, charges, revenue, users."""
from config import ApiError
from models.account import UserRepo

class AdminOperations:
    """view_all_bookings, approve/reject, check_in, check_out, add_incidental_charge, view_revenue, manage_user"""
    def view_all_bookings(self): return [self.ctx.book.dto(b) for b in self.ctx.bookings.newest()]
    def approve_booking(self, booking_id): self.ctx.book.admin_action(booking_id, 'approve', {}); return True
    def reject_booking(self, booking_id): self.ctx.book.admin_action(booking_id, 'reject', {}); return True
    def add_incidental_charge(self, booking_id, charge, reason): self.ctx.book.admin_action(booking_id, 'charge', {'amount': charge, 'reason': reason})
    def view_revenue(self): return self.ctx.book.revenue()
    def check_in(self, booking_id, identity_card): self.ctx.book.admin_action(booking_id, 'checkin', {'idcard': identity_card})
    def check_out(self, booking_id): self.ctx.book.admin_action(booking_id, 'checkout', {})
    def manage_user(self, action='list', user_id=None, data=None):
        if action == 'list': return [UserRepo.public(x) for x in self.ctx.users.customers()]
        if action == 'lock': self.ctx.users.toggle_lock(user_id); return True
        if action == 'create': self.ctx.book.create_customer(data or {}); return True
        raise ApiError('Unknown action')
