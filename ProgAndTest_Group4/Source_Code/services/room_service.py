"""Room list, search / filter and room detail."""
import re, difflib, datetime as dt
from config import Config, num, today
from models.room import Room
from config import ApiError

class RoomService:
    def __init__(self, rooms, services, bookings, reviews): self.rooms, self.services, self.bookings, self.reviews = rooms, services, bookings, reviews
    def dto(self, r, a=None, b=None):
        d = dict(r); d['rating'], d['reviews'] = self.rooms.rating(r['id'])
        a, b = (a, b) if a and b else (today().isoformat(), (today() + dt.timedelta(1)).isoformat())
        d['free'] = Room.from_row(r).is_available(a, b)
        d['services'] = [dict(s) for s in self.services.all() if s['code'] in (r['svc'] or '').split(',')]; return d
    def check_dates(self, cin, cout):
        """If both dates are given and check-in is later than check-out, stop with an error message."""
        try: a, b = dt.date.fromisoformat(cin), dt.date.fromisoformat(cout)
        except (TypeError, ValueError): return          # empty or badly typed dates are ignored, as before
        if a > b: raise ApiError('Check-in date cannot be later than check-out date')
        if a == b: raise ApiError('Check-out must be at least 1 day after check-in')
    def search(self, a):
        self.check_dates(a.get('cin'), a.get('cout'))
        kw = (a.get('q') or a.get('code') or '').lower().strip(); out = []
        for r in self.rooms.all():
            t = (r['code'] + r['type'] + (r['descr'] or '')).lower()
            if kw and kw not in t and not any(difflib.SequenceMatcher(None, kw, w).ratio() > .6 for w in re.findall(r'\w+', t)): continue
            if num(a.get('min')) > 0 and r['price'] < num(a['min']): continue      # 0 / empty = no price filter
            if num(a.get('max')) > 0 and r['price'] > num(a['max']): continue
            if a.get('cap') and r['cap'] < int(num(a['cap'])): continue
            d = self.dto(r, a.get('cin'), a.get('cout'))
            if a.get('avail') == '1' and not d['free']: continue
            if a.get('avail') == '0' and d['free']: continue
            if a.get('stars') and d['rating'] < num(a['stars']): continue
            out.append(d)
        p = max(1, int(num(a.get('page')) or 1)); n = Config.PAGE
        return dict(rooms=out[(p - 1) * n:p * n], total=len(out), pages=max(1, -(-len(out) // n)))
    def detail(self, code, user):
        r = self.rooms.get(code)
        if not r: raise ApiError('Not found', 404)
        d = self.dto(r); d['list'] = [dict(x) for x in self.reviews.for_room(r['id'])]
        d['canReview'] = bool(user and self.bookings.db.q("select 1 from bookings b where uid=? and rid=? and status='completed' and not exists(select 1 from reviews where bid=b.id)", (user['id'], r['id']), True)); return d
