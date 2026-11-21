"""My bookings, cancel (+ refund), add service, review."""
from flask import render_template, request, redirect, url_for, flash
from controllers.blueprints import customer_bp
from controllers.helpers import hotel, save_image, current_customer

@customer_bp.get('/my')
def my_bookings(): return render_template('my_bookings.html', bookings=current_customer().view_booking_history())

@customer_bp.route('/my/<code>/cancel', methods=['GET', 'POST'])
def cancel(code):
    c = current_customer()
    if request.method == 'GET': return render_template('cancel.html', b=hotel().book.one(c.user, code))
    c.cancel_booking(code); flash(f'Cancelled. Refunded ${c.last_refund}' if c.last_refund else 'Booking cancelled (no refund: the free-cancellation period has passed or nothing was paid).', 'ok')
    return redirect(url_for('customer.my_bookings'))

@customer_bp.route('/my/<code>/service', methods=['GET', 'POST'])
def add_service(code):
    c = current_customer()
    if request.method == 'GET': return render_template('add_service.html', b=hotel().book.one(c.user, code), services=hotel().services.all())
    c.add_service(code, request.form.get('service')); flash('Service added', 'ok'); return redirect(url_for('customer.my_bookings'))

@customer_bp.route('/review/<code>', methods=['GET', 'POST'])
def review(code):
    c = current_customer(); room = c.view_room_detail(code)
    if request.method == 'GET': return render_template('review.html', room=room)
    f = request.form; c.write_review(room['id'], f.get('stars'), f.get('text'), save_image(request.files.get('image')), request.args.get('b'))
    flash('Thank you for your review!', 'ok'); return redirect(url_for('guest.room_detail', code=code))
