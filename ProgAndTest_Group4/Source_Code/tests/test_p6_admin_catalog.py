"""Person 6 – Admin catalog: rooms, room types, services, vouchers, image upload + project rules.   Run:  pytest tests/test_p6_admin_catalog.py -v"""
import pytest
import io
import os
import glob
import app
from config import ApiError
from helpers import customer, admin, book, row, login

ROOM = {'code': '999-NEW', 'type': 'DLX', 'price': 50, 'area': 20, 'cap': 2, 'descr': 't', 'img': 'r1.jpg', 'svc': ''}
def test_admin_manage_room(h): a = admin(h); assert a.manage_room('save', ROOM) and a.manage_room('delete', key='999-NEW')
def test_admin_room_unknown_type_rejected(h):
    with pytest.raises(ApiError, match='room type'): admin(h).manage_room('save', {**ROOM, 'type': 'ZZZ'})
def test_admin_cannot_delete_room_with_active_booking(h):
    book(customer(h))
    with pytest.raises(ApiError): admin(h).manage_room('delete', key='302-DLX')
def test_admin_manage_room_type(h):
    a = admin(h); assert a.manage_room_type('save', {'type_id': 'FAM', 'type_name': 'Family', 'description': ''})
    with pytest.raises(ApiError, match='in use'): a.manage_room_type('delete', key='DLX')
    assert a.manage_room_type('delete', key='FAM')
def test_admin_manage_service(h): a = admin(h); a.manage_service('save', {'code': 'S999', 'name': 'Gym', 'price': 5, 'descr': ''}); assert any(s['code'] == 'S999' for s in a.manage_service('list'))
def test_admin_voucher_validation(h):
    with pytest.raises(ApiError): admin(h).manage_voucher('save', {'code': 'X', 'pct': 150, 'start': '2026-01-01', 'end': '2026-02-01'})
def test_admin_voucher_disable_toggle(h): admin(h).manage_voucher('delete', key='WELCOME10'); assert row(h.vouchers, 'WELCOME10')['active'] == 0
def test_admin_can_upload_room_image_from_computer(client):
    login(client, 'admin@hotel.com', 'Admin@123')
    client.post('/admin/rooms', data={'code': '999-NEW', 'type': 'DLX', 'price': '50', 'area': '20', 'cap': '2', 'descr': 't', 'svc': '', 'image': (io.BytesIO(b'\x89PNG'), 'a.png')}, content_type='multipart/form-data')
    page = client.get('/admin/rooms').data; assert b'999-NEW' in page and b'uploads/' in client.get('/rooms/999-NEW').data
    for f in glob.glob(os.path.join(app.A.root_path, 'static', 'uploads', '*')): os.remove(f)
def test_project_uses_only_html_css_python():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assert not [f for f in glob.glob(root + '/**/*.js', recursive=True) if '.venv' not in f]
    for f in glob.glob(root + '/templates/**/*.html', recursive=True):
        text = open(f, encoding='utf8').read().lower(); assert '<script' not in text and ' onclick=' not in text and ' onsubmit=' not in text, f
