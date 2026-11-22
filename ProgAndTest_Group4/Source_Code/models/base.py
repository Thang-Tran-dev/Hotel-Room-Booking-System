"""Base classes: Entity (class-diagram objects) and Repository (generic SQL access)."""
from config import ApiError

class Entity:
    ctx = None            
    FIELDS = {}           
    def __init__(self, **kw):
        for a in self.FIELDS: setattr(self, a, None)
        self.__dict__.update(kw); self.row = None
    @classmethod
    def from_row(cls, r):
        o = cls(); o.row = r; keys = r.keys()
        for a, c in cls.FIELDS.items():
            if c in keys: setattr(o, a, r[c])
        return o

class Repository:
    table = key = None; cols = ()
    def __init__(self, db): self.db = db
    def all(self): return self.db.q(f'select * from {self.table}')
    def get(self, v, col=None): return self.db.q(f'select * from {self.table} where {col or self.key}=?', (v,), True)
    def add(self, d, commit=True):
        k = list(d); self.db.q(f'insert into {self.table}({",".join(k)}) values({",".join("?" * len(k))})', [d[x] for x in k], commit=commit)
    def set(self, key, d):
        k = list(d); self.db.q(f'update {self.table} set ' + ','.join(x + '=?' for x in k) + f' where {self.key}=?', [d[x] for x in k] + [key])
    def validate(self, d):
        if not d.get(self.key): raise ApiError('Code is required')
    def save(self, d):
        self.validate(d); self.set(d[self.key], d) if self.get(d[self.key]) else self.add(d)
    def remove(self, v): self.db.q(f'delete from {self.table} where {self.key}=?', (v,))
