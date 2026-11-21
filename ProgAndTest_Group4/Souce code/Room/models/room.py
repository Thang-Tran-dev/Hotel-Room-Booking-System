"""Room, RoomType, Service entities + their repositories."""
import datetime as dt
from config import ApiError, today
from models.base import Entity, Repository

class RoomType(Entity): FIELDS = {'type_id': 'type_id', 'type_name': 'type_name', 'description': 'description'}

class Service(Entity): FIELDS = {'service_id': 'code', 'service_name': 'name', 'service_price': 'price', 'description': 'descr'}

class Room(Entity):
    FIELDS = {'room_id': 'id', 'room_number': 'code', 'type_id': 'type', 'price_per_night': 'price', 'capacity': 'cap', 'area': 'area', 'description': 'descr', 'image': 'img'}
    def get_room_detail(self): return self.ctx.room_svc.detail(self.room_number, None)
    def is_available(self, check_in_date=None, check_out_date=None):
        import datetime as dt
        a, b = check_in_date or today().isoformat(), check_out_date or (today() + dt.timedelta(1)).isoformat()
        return not self.ctx.bookings.busy(self.room_id, a, b)

class ServiceRepo(Repository): table, key, cols = 'services', 'code', ('code', 'name', 'price', 'descr')

class RoomRepo(Repository):
    table, key, cols = 'rooms', 'code', ('code', 'type', 'price', 'area', 'cap', 'descr', 'img', 'svc')
    def validate(self, d):
        super().validate(d)
        if not self.db.q('select 1 from roomtypes where type_id=?', (d.get('type'),), True): raise ApiError('Unknown room type')
    def rating(self, rid):
        r = self.db.q('select avg(stars) a,count(*) c from reviews where rid=?', (rid,), True); return (round(r['a'], 1) if r['a'] else 0), r['c']
    def remove(self, v):
        if self.db.q("select 1 from bookings b join rooms r on r.id=b.rid where r.code=? and b.status in('pending','confirmed','checkedin')", (v,), True):
            raise ApiError('Room has active bookings and cannot be deleted')
        super().remove(v)

class RoomTypeRepo(Repository):
    table, key, cols = 'roomtypes', 'type_id', ('type_id', 'type_name', 'description')
    def remove(self, v):
        if self.db.q('select 1 from rooms where type=?', (v,), True): raise ApiError('Room type is in use')
        super().remove(v)
