"""Application entry point.
Wiring (bottom → top):  models (data + class-diagram entities) → services (business rules) → controllers (HTTP) → templates (HTML) + static/css."""
import os
from flask import Flask
from config import Config, ApiError
from models.base import Entity
from models.database import Database
from models.mailer import Mailer
from models.account import UserRepo
from models.room import RoomRepo, ServiceRepo, RoomTypeRepo
from models.booking import VoucherRepo, BookingRepo, BookingDetailRepo, PaymentRepo, InvoiceRepo
from models.review import ReviewRepo
from services.auth_service import AuthService
from services.pricing_service import PricingService
from services.room_service import RoomService
from services.booking_service import BookingService
from controllers import auth, account, rooms, booking, my_bookings, admin_operations, admin_catalog   # importing them registers their pages
from controllers.blueprints import guest_bp, customer_bp, admin_bp
from controllers.helpers import setup_web

class Hotel:
    """Creates every repository and service once and hands them to controllers / entities (`current_app.hotel`)."""
    def __init__(self):
        self.db, self.mail = Database(), Mailer(); db = self.db
        self.users, self.rooms, self.services, self.vouchers, self.bookings, self.reviews = UserRepo(db), RoomRepo(db), ServiceRepo(db), VoucherRepo(db), BookingRepo(db), ReviewRepo(db)
        self.roomtypes, self.details, self.payments, self.invoices = RoomTypeRepo(db), BookingDetailRepo(db), PaymentRepo(db), InvoiceRepo(db)
        self.auth = AuthService(self.users, self.mail); self.pricing = PricingService(self.rooms, self.services, self.vouchers)
        self.room_svc = RoomService(self.rooms, self.services, self.bookings, self.reviews)
        self.book = BookingService(db, self.bookings, self.rooms, self.users, self.services, self.reviews, self.pricing, self.mail, self.details, self.payments, self.invoices)

def create_app():
    app = Flask(__name__)                                   # templates/ and static/ are found automatically
    app.secret_key = Config.secret(); app.config.update(MAX_CONTENT_LENGTH=5 * 1024 * 1024, SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax')
    app.hotel = Hotel(); Entity.ctx = app.hotel; app.teardown_appcontext(app.hotel.db.close)
    setup_web(app)
    for blueprint in (guest_bp, customer_bp, admin_bp): app.register_blueprint(blueprint)
    return app

A = create_app(); hotel = A.hotel           # `A` is the WSGI object used by wsgi.py / PythonAnywhere / gunicorn
hotel.db.setup()                            # create tables + sample data on first start (and upgrade old databases)
if __name__ == '__main__': A.run(debug=os.environ.get('DEBUG') == '1', port=int(os.environ.get('PORT', 5000)))
