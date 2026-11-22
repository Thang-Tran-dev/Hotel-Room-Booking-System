"""Guest operations about rooms: list, detail, search, filter."""


class GuestRooms:
    """view_room_list, view_room_detail, search_room, filter_room"""
    def view_room_list(self, page=1): return self.ctx.room_svc.search({'page': page})
    def view_room_detail(self, room_id): return self.ctx.room_svc.detail(room_id, self.ctx.auth.current())
    def search_room(self, keyword='', check_in_date=None, check_out_date=None, number_of_guest=None, **filters):
        return self.ctx.room_svc.search({'q': keyword, 'cin': check_in_date, 'cout': check_out_date, 'cap': number_of_guest, **filters})
    def filter_room(self, min_price=0, max_price=0, availability=None, **extra):
        return self.ctx.room_svc.search({'min': min_price, 'max': max_price, 'avail': '' if availability is None else ('1' if availability else '0'), **extra})
