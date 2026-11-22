"""Book a room: room page → booking summary (+ voucher) → confirm → payment → success."""
import re
from config import ApiError, Config
from flask import render_template, request, redirect, url_for, flash, session
from controllers.blueprints import customer_bp
from controllers.helpers import hotel, require_login, qr_svg, current_customer

def whole_number(text, label):
    """'' -> 0; 'abc' or '1.5' -> a friendly error instead of a crash."""
    try: return int((text or '0').strip() or 0)
    except ValueError: raise ApiError(f'{label} must be a whole number')

def draft():
    d = session.get('draft')
    if not d: raise ApiError('Please choose a room first')
    return d

@customer_bp.post('/book/<code>')
def start_booking(code):
    current_customer(); f = request.form; room = hotel().rooms.get(code)
    if not room: raise ApiError('Not found', 404)
    adults, kids = whole_number(f.get('adults'), 'Number of adults'), whole_number(f.get('kids'), 'Number of children'); hotel().book.check_guests(room, adults, kids); hotel().book.check_stay(f.get('cin'), f.get('cout'))       # stop here (back on the room page) instead of at the last step
    session['draft'] = dict(rid=room['id'], cin=f.get('cin'), cout=f.get('cout'), adults=adults, kids=kids, svc=[f['service']] if f.get('service') else [], vouchers=[])
    return redirect(url_for('customer.booking'))

@customer_bp.get('/booking')
def booking():
    current_customer(); d = draft(); h = hotel()
    p = h.pricing.quote(d['rid'], d['cin'], d['cout'], d['svc'], d['vouchers'])
    return render_template('booking.html', d=d, p=p, room=h.room_svc.dto(h.rooms.get(d['rid'], 'id')))

@customer_bp.post('/booking/voucher')
def add_voucher():
    c = current_customer(); d = draft(); code = (request.form.get('voucher') or '').strip().upper()
    if not c.apply_voucher(code): raise ApiError(f'Voucher {code} is invalid or expired')
    if code not in d['vouchers']: d['vouchers'].append(code); session.modified = True
    flash(f'Voucher {code} applied', 'ok'); return redirect(url_for('customer.booking'))

@customer_bp.post('/booking/confirm')
def confirm_booking():
    c = current_customer(); d = draft(); f = request.form
    if not f.get('name') or not Config.EMAIL.match(f.get('email') or '') or not Config.PHONE.match(f.get('phone') or ''): raise ApiError('Invalid guest information')
    c.select_room(d['rid'], d['cin'], d['cout'])
    b = c.create_booking(d['adults'], d['kids'], d['svc'], d['vouchers'], f"Guest: {f['name']} {f['phone']}")
    session.pop('draft', None); session['pay_pref'] = f.get('pm'); return redirect(url_for('customer.pay', code=b['code']))

@customer_bp.route('/pay/<code>', methods=['GET', 'POST'])
def pay(code):
    c = current_customer(); h = hotel(); b = h.book.one(c.user, code)
    if request.method == 'POST':
        f = request.form
        if f.get('method') == 'card' and not (f.get('holder') and re.fullmatch(r'[\d\s]{12,19}', f.get('number', '')) and re.fullmatch(r'\d\d\s*/\s*\d\d', f.get('expiry', '')) and re.fullmatch(r'\d{3,4}', f.get('cvv', ''))):
            raise ApiError('Please enter valid payment details')
        c.pay(code, f.get('method')); return redirect(url_for('customer.success', code=code))
    if b['status'] != 'pending': return redirect(url_for('customer.my_bookings'))
    p = h.pricing.quote(b['rid'], b['cin'], b['cout'], [x for x in b['svc'].split(',') if x], [x for x in b['voucher'].split(',') if x], b['extra'])
    return render_template('payment.html', b=b, p=p, room=h.room_svc.dto(h.rooms.get(b['rid'], 'id')), pref=session.get('pay_pref'), hold_until=(b['hold'] or '')[11:19], qr=qr_svg(f"MOMO|{code}|{b['deposit']}"))

@customer_bp.get('/success/<code>')
def success(code):
    b = hotel().book.one(require_login(), code); return render_template('success.html', b=b, at_hotel=b['method'] == 'hotel')
