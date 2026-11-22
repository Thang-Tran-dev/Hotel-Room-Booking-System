"""Customer profile and change password."""
from flask import render_template, request, redirect, url_for, flash
from controllers.blueprints import customer_bp
from controllers.helpers import current_customer

@customer_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    c = current_customer()
    if request.method == 'POST':
        f = request.form; c.update_profile(f.get('name'), f.get('phone'), f.get('idcard'), f.get('address'), f.get('sex'), f.get('dob')); flash('Changes saved', 'ok'); return redirect(url_for('customer.profile'))
    return render_template('profile.html', p=c.view_profile())

@customer_bp.route('/password', methods=['GET', 'POST'])
def password():
    c = current_customer()
    if request.method == 'GET': return render_template('password.html')
    f = request.form; c.account.change_password(f.get('old'), f.get('new'), f.get('new2'))
    flash('Password changed. A notification email has been sent.', 'ok'); return redirect(url_for('guest.home'))
