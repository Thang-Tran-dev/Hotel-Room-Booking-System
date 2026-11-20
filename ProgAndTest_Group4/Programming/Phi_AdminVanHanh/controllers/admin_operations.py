"""Admin: bookings, check-in / check-out / charges, revenue, users."""
from config import ApiError
from flask import render_template, request, redirect, url_for
from controllers.blueprints import admin_bp
from controllers.helpers import current_admin, done

@admin_bp.get('/')
def index(): return redirect(url_for('admin.bookings'))

@admin_bp.get('/bookings')
def bookings():
    f = request.args; q = (f.get('q') or '').lower()
    rows = [b for b in current_admin().view_all_bookings() if (not q or q in (b['code'] + b['cust']).lower()) and (not f.get('status') or b['status'] == f['status'])
            and (not f.get('d1') or b['cin'] >= f['d1']) and (not f.get('d2') or b['cin'] <= f['d2'])]
    if f.get('sort') == 'cin': rows.sort(key=lambda b: b['cin'])
    return render_template('admin/bookings.html', rows=rows, args=f, active='bookings', statuses=['pending', 'confirmed', 'checkedin', 'completed', 'cancelled'])

@admin_bp.post('/bookings/<code>/<act>')
def booking_action(code, act):
    a, f = current_admin(), request.form
    if act == 'approve': a.approve_booking(code)
    elif act == 'reject': a.reject_booking(code)
    elif act == 'checkin': a.check_in(code, f.get('idcard'))
    elif act == 'checkout': a.check_out(code)
    elif act == 'charge': a.add_incidental_charge(code, f.get('amount') or -1, f.get('reason'))
    else: raise ApiError('Unknown action')
    return done()

@admin_bp.get('/revenue')
def revenue(): return render_template('admin/revenue.html', data=current_admin().view_revenue(), active='revenue')

@admin_bp.get('/users')
def users(): return render_template('admin/users.html', users=current_admin().manage_user('list'), active='users')

@admin_bp.post('/users/<int:i>/lock')
def lock_user(i): current_admin().manage_user('lock', user_id=i); return done()

@admin_bp.route('/users/new', methods=['GET', 'POST'])
def user_new():
    a = current_admin()
    if request.method == 'GET': return render_template('admin/user_new.html', rooms=a.manage_room('list'), active='users')
    f = request.form.to_dict(); f['rid'] = int(f['rid']) if f.get('rid') else None; f['adults'] = int(f.get('adults') or 1); f['kids'] = int(f.get('kids') or 0)
    a.manage_user('create', data=f); return done('Account created' + (' and booking made (pay at hotel)' if f['rid'] else ''), url_for('admin.users'))
