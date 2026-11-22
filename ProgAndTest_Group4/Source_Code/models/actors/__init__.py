"""Actors of the class diagram: Guest ◁ Customer, Guest ◁ Admin. Each actor is assembled from small mixins (one file per owner)."""
from models.account import Account
from models.actors.guest_account import GuestAccount
from models.actors.guest_rooms import GuestRooms
from models.actors.customer_account import CustomerAccount
from models.actors.customer_booking import CustomerBooking
from models.actors.customer_after_booking import CustomerAfterBooking
from models.actors.admin_operations import AdminOperations
from models.actors.admin_catalog import AdminCatalog

class Guest(GuestRooms, GuestAccount):
    """Guest (anyone) – operations are split in guest_rooms.py and guest_account.py."""
    def __init__(self, ctx): self.ctx = ctx

class Customer(CustomerAccount, CustomerBooking, CustomerAfterBooking, Guest):
    """Customer ◁ Guest – operations are split in customer_account / customer_booking / customer_after_booking."""
    def __init__(self, ctx, row):
        super().__init__(ctx); self.user, self.account = row, Account.from_row(row); self.customer_id = row['id']
        self.sex, self.identity_card, self.address, self.date_of_birth = row['sex'], row['idcard'], row['address'], row['dob']
        self._selection, self.last_refund = None, 0

class Admin(AdminOperations, AdminCatalog, Guest):
    """Admin ◁ Guest – operations are split in admin_operations.py and admin_catalog.py."""
    def __init__(self, ctx, row): super().__init__(ctx); self.user, self.admin_id = row, row['id']
