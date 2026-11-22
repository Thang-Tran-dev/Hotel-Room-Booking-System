"""Admin operations: manage rooms, room types, services, vouchers."""
from config import ApiError

class AdminCatalog:
    """manage_room, manage_room_type, manage_service, manage_voucher"""
    @staticmethod
    def _crud(repo, action, data, key):
        if action == 'list': return [dict(x) for x in repo.all()]
        if action == 'save': repo.save({c: (data or {}).get(c) for c in repo.cols}); return True
        if action == 'delete': repo.remove(key); return True
        raise ApiError('Unknown action')
    def manage_service(self, action='list', data=None, key=None): return self._crud(self.ctx.services, action, data, key)
    def manage_room(self, action='list', data=None, key=None): return self._crud(self.ctx.rooms, action, data, key)
    def manage_room_type(self, action='list', data=None, key=None): return self._crud(self.ctx.roomtypes, action, data, key)
    def manage_voucher(self, action='list', data=None, key=None): return self._crud(self.ctx.vouchers, action, data, key)
