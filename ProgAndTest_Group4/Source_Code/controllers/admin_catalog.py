"""Admin: rooms (+ room types, image upload), vouchers, services."""
from flask import render_template, request, url_for
from models.booking import Voucher
from controllers.blueprints import admin_bp
from controllers.helpers import save_image, current_admin, done

@admin_bp.get('/rooms')
def rooms():
    a = current_admin(); items = a.manage_room('list'); e = next((r for r in items if r['code'] == request.args.get('edit')), None)
    return render_template('admin/rooms.html', rooms=items, types=a.manage_room_type('list'), e=e, active='rooms')

@admin_bp.post('/rooms')
def save_room():
    f = request.form.to_dict(); f['img'] = save_image(request.files.get('image')) or f.get('img') or 'r1.jpg'
    current_admin().manage_room('save', f); return done('Room saved', url_for('admin.rooms'))

@admin_bp.post('/rooms/<code>/delete')
def delete_room(code): current_admin().manage_room('delete', key=code); return done('Room deleted', url_for('admin.rooms'))

@admin_bp.post('/roomtypes')
def add_room_type(): f = request.form; current_admin().manage_room_type('save', {'type_id': f.get('type_id', '').strip().upper(), 'type_name': f.get('type_name'), 'description': ''}); return done('Room type added', url_for('admin.rooms'))

@admin_bp.get('/vouchers')
def vouchers():
    a = current_admin(); items = [dict(v, state=('still valid' if Voucher.from_row(v).is_valid() else 'invalid')) for v in a.manage_voucher('list')]
    return render_template('admin/vouchers.html', vouchers=items, e=next((v for v in items if v['code'] == request.args.get('edit')), None), active='vouchers')

@admin_bp.post('/vouchers')
def save_voucher(): current_admin().manage_voucher('save', request.form.to_dict()); return done('Voucher saved', url_for('admin.vouchers'))

@admin_bp.post('/vouchers/<code>/toggle')
def toggle_voucher(code): current_admin().manage_voucher('delete', key=code); return done('Voucher updated', url_for('admin.vouchers'))

@admin_bp.get('/services')
def services():
    items = current_admin().manage_service('list'); return render_template('admin/services.html', services=items, e=next((s for s in items if s['code'] == request.args.get('edit')), None), active='services')

@admin_bp.post('/services')
def save_service(): current_admin().manage_service('save', request.form.to_dict()); return done('Service saved', url_for('admin.services'))

@admin_bp.post('/services/<code>/delete')
def delete_service(code): current_admin().manage_service('delete', key=code); return done('Service deleted', url_for('admin.services'))
