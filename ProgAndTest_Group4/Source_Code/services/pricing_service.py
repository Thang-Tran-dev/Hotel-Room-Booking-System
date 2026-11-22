"""Price calculation: nights × price + services − vouchers + VAT, deposit 30 %."""
import datetime as dt
from config import Config, ApiError
from models.booking import Voucher

class PricingService:
    def __init__(self, rooms, services, vouchers): self.rooms, self.services, self.vouchers = rooms, services, vouchers
    def quote(self, rid, cin, cout, svc, codes, extra=0):
        r = self.rooms.get(rid, 'id')
        try: n = (dt.date.fromisoformat(cout) - dt.date.fromisoformat(cin)).days
        except (TypeError, ValueError): raise ApiError('Invalid date range')
        if not r: raise ApiError('Not found', 404)
        if n < 1: raise ApiError('Check-out must be after check-in')
        s = sum(x['price'] for x in self.services.all() if x['code'] in svc); base = r['price'] * n; pc = 0
        for c in codes:
            v = self.vouchers.get(c)
            if not v or not Voucher.from_row(v).is_valid(): raise ApiError(f'Voucher {c} is invalid or expired')
            pc += v['pct']
        disc = round((base + s) * min(pc, 100) / 100, 2); vat = round((base + s - disc) * Config.VAT, 2); tot = round(base + s - disc + vat + extra, 2)
        return dict(nights=n, room=base, extra_service=s, discount=disc, vat=vat, total=tot, deposit=round(tot * Config.DEPOSIT, 2), remaining=round(tot * (1 - Config.DEPOSIT), 2))
