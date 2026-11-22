"""Customer operations after booking: history, cancel, review, add service."""


class CustomerAfterBooking:
    """view_booking_history, cancel_booking, write_review, add_service"""
    def view_booking_history(self): return self.ctx.book.mine(self.user)
    def cancel_booking(self, booking_id): self.last_refund = self.ctx.book.cancel(self.user, booking_id); return True
    def write_review(self, room_id, rating, content, image=None, booking_code=None):
        code = booking_code or self.ctx.book.reviewable(self.user, room_id)
        self.ctx.book.review(self.user, dict(code=code, stars=rating, text=content, img=image)); return True
    def add_service(self, booking_id, service_id): return self.ctx.book.add_service(self.user, booking_id, service_id)
