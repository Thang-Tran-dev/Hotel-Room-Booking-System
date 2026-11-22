"""Sign in, sign up, forgot password, logout."""
from flask import render_template, request, redirect, url_for, flash
from models.account import Account
from controllers.blueprints import guest_bp
from controllers.helpers import hotel
from models.actors import Guest

@guest_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET': return render_template('auth/login.html')
    f = request.form; who = Guest(hotel()).sign_in(f.get('email'), f.get('pw'), bool(f.get('remember')))
    nxt = f.get('next') or ''
    if nxt.startswith('/') and not nxt.startswith('//'): return redirect(nxt)
    return redirect(url_for('admin.bookings') if who.user['role'] == 'admin' else url_for('guest.home'))

@guest_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET': return render_template('auth/signup.html')
    f = request.form; Guest(hotel()).sign_up(f.get('name'), f.get('pw'), f.get('email'), f.get('phone'), f.get('pw2'))
    flash('Registration successful! Please sign in.', 'ok'); return redirect(url_for('guest.login'))

@guest_bp.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == 'GET': return render_template('auth/forgot.html')
    Account().reset_password(request.form.get('email')); flash('A new password has been sent to your email (see emails.log).', 'ok')
    return redirect(url_for('guest.login'))

@guest_bp.post('/logout')
def logout(): Account().logout(); return redirect(url_for('guest.home'))
