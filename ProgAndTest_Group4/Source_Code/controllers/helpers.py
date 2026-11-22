"""Small helpers shared by all controllers: login checks, image upload, QR code, template filters, error handling."""
import os, random, string
from urllib.parse import urlparse
from flask import current_app, flash, redirect, request, url_for
from markupsafe import Markup
from config import Config, ApiError
from models.actors import Customer, Admin

def hotel(): return current_app.hotel                    # the object that wires repositories + services (see app.py)
def current_user(): return hotel().auth.current()
def require_login(): return hotel().auth.require()
def require_admin(): return hotel().auth.require(admin=True)
def current_customer(): return Customer(hotel(), require_login())      # the signed-in customer as a Customer object
def current_admin(): return Admin(hotel(), require_admin())            # the signed-in admin as an Admin object
def done(msg='Done', to=None):
    """Green message + go back (used by admin forms)."""
    flash(msg, 'ok'); return redirect(to or request.referrer or url_for('admin.bookings'))

def save_image(file_storage):
    """Save an uploaded image into static/uploads and return its path ('uploads/xxx.png'), or None if no file was chosen."""
    if not file_storage or not file_storage.filename: return None
    ext = os.path.splitext(file_storage.filename)[1].lower()
    if ext not in Config.IMAGES: raise ApiError('Please choose an image file (png, jpg, gif, webp)')
    folder = os.path.join(current_app.root_path, 'static', 'uploads'); os.makedirs(folder, exist_ok=True)
    name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12)) + ext
    file_storage.save(os.path.join(folder, name)); return 'uploads/' + name

def save_images(files, limit=None):
    """Save several uploaded images (the review form) and return their paths joined by commas ('uploads/a.png,uploads/b.jpg'), or None if nothing was chosen."""
    files = [f for f in files if f and f.filename]; limit = limit or Config.REVIEW_IMAGES
    if len(files) > limit: raise ApiError(f'You can add up to {limit} images')
    if any(os.path.splitext(f.filename)[1].lower() not in Config.IMAGES for f in files): raise ApiError('Please choose image files (png, jpg, gif, webp)')   # check all first, so nothing is half-saved
    return ','.join(save_image(f) for f in files) or None

def qr_svg(text):
    """QR code as inline SVG (needs the small pure-Python package `segno`); returns None if it is not installed."""
    try: import segno
    except ImportError: return None
    return Markup(segno.make(text, error='m').svg_inline(scale=5, border=1))

def money(x):
    s = f'{float(x or 0):.2f}'; return '$' + (s[:-3] if s.endswith('.00') else s)

def room_image(path):
    path = path or 'r1.jpg'; return url_for('static', filename=path if path.startswith('uploads/') else 'images/' + path)

def setup_web(app):
    """Register Jinja filters, values available in every template, and the single error handler."""
    import datetime as dt
    app.add_template_filter(money, 'money'); app.add_template_filter(room_image, 'room_image')
    @app.context_processor
    def common():
        u = current_user(); t = dt.date.today()
        return {'user': dict(u) if u else None, 'today': t.isoformat(), 'tomorrow': (t + dt.timedelta(1)).isoformat()}
    @app.errorhandler(ApiError)
    def show_error(e):                                    
        flash(e.msg, 'error')
        if e.code == 401:
            back = urlparse(request.referrer or '').path if request.method == 'POST' else request.full_path.rstrip('?')
            return redirect(url_for('guest.login', next=back or ''))
        if e.code == 403: return redirect(url_for('guest.home'))
        return redirect(request.referrer or url_for('guest.home'))
