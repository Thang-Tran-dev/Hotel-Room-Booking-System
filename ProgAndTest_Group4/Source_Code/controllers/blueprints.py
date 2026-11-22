"""The three blueprints (groups of pages). Every controller file adds its pages to one of them."""
from flask import Blueprint

guest_bp = Blueprint('guest', __name__)            # anyone: home, rooms, sign in / up
customer_bp = Blueprint('customer', __name__)      # signed-in customers
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
