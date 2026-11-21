"""Home page, room list and room detail."""
from flask import render_template, request, url_for
from controllers.blueprints import guest_bp
from controllers.helpers import hotel
from models.actors import Guest

@guest_bp.get('/')
def home(): return render_template('home.html')

@guest_bp.get('/rooms')
def rooms():
    a = request.args
    result = Guest(hotel()).search_room(a.get('q'), a.get('cin'), a.get('cout'), a.get('cap'), **{k: a[k] for k in ('min', 'max', 'avail', 'stars', 'page') if a.get(k)})
    page = int(a.get('page') or 1)
    links = [(n, url_for('guest.rooms', **{**a.to_dict(), 'page': n})) for n in range(1, result['pages'] + 1)]
    return render_template('rooms.html', result=result, page=page, links=links, args=a)

@guest_bp.get('/rooms/<code>')
def room_detail(code): return render_template('room_detail.html', room=Guest(hotel()).view_room_detail(code))
