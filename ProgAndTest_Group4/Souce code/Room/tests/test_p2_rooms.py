"""Person 2 – Rooms: list, detail, search, filter.   Run:  pytest tests/test_p2_rooms.py -v"""
import pytest
from config import ApiError
from models.actors import Guest
from helpers import d, customer, PUBLIC

def test_view_room_list(h): assert Guest(h).view_room_list()['total'] == 4
def test_view_room_detail(h): assert Guest(h).view_room_detail('302-DLX')['code'] == '302-DLX'
def test_view_room_detail_not_found(h):
    with pytest.raises(ApiError): Guest(h).view_room_detail('nope')
def test_search_room_by_keyword(h): assert [r['code'] for r in Guest(h).search_room('DLX')['rooms']] == ['302-DLX']
def test_filter_price_zero_means_no_filter(h): assert Guest(h).filter_room(0, 0)['total'] == 4
def test_filter_min_price(h): assert Guest(h).filter_room(90, 0)['total'] == 2
def test_filter_availability(h):
    c = customer(h); c.select_room(1, d(0), d(1)); c.create_booking(1, 0); assert Guest(h).filter_room(availability=True)['total'] == 3
def test_public_pages_open(client): assert all(client.get(u).status_code == 200 for u in PUBLIC)
