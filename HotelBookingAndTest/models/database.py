"""Database connection, table creation / migration, sample data, and the (simulated) e-mail sender."""
import os, sqlite3, datetime as dt
from flask import g
from werkzeug.security import generate_password_hash as H
from config import BASE, Config

# ───────────── Infrastructure ─────────────
class Database:
    SCHEMA = '''
create table if not exists users(id integer primary key,name,email unique,phone,pw,role default 'customer',locked int default 0,fails int default 0,idcard,address,dob,sex);
create table if not exists rooms(id integer primary key,code unique,type,price real,area real,cap int,descr,img,svc default '',beds default 'King Bed',view default 'Ocean View');
create table if not exists services(id integer primary key,code unique,name,price real,descr);
create table if not exists vouchers(id integer primary key,code unique,pct real,start,end,cond,active int default 1);
create table if not exists bookings(id integer primary key,code unique,uid,rid,cin,cout,adults,kids,svc default '',voucher default '',total real,deposit real,status default 'pending',paid int default 0,method,extra real default 0,vat real default 0,discount real default 0,notes default '',hold text,created text);
create table if not exists reviews(id integer primary key,uid,rid,bid unique,stars int,text,img,at text);
create table if not exists roomtypes(id integer primary key,type_id unique,type_name,description);
create table if not exists booking_details(id integer primary key,detail_id unique,bcode,rid,nights int,room_price real,sub_total real);
create table if not exists payments(id integer primary key,payment_id unique,bcode,amount real,method,paid_at text,status,refund_amount real default 0);
create table if not exists invoices(id integer primary key,invoice_id unique,bcode,issued text,total_amount real);'''
    def conn(self):
        if 'd' not in g: g.d = sqlite3.connect(Config.DB); g.d.row_factory = sqlite3.Row
        return g.d
    def close(self, _=None):
        d = g.pop('d', None)
        if d: d.close()
    def q(self, sql, args=(), one=False, commit=True):
        c = self.conn().execute(sql, args)
        if commit: self.conn().commit()
        r = c.fetchall(); return (r[0] if r else None) if one else r
    def begin(self): self.conn().execute('begin immediate')
    def commit(self): self.conn().commit()
    def rollback(self): self.conn().rollback()
    def setup(self):
        d = sqlite3.connect(Config.DB); d.executescript(self.SCHEMA)
        if not d.execute('select 1 from users').fetchone():
            d.execute("insert into users(name,email,phone,pw,role) values('Admin','admin@hotel.com','0900000000',?,'admin')", (H(Config.ADMIN_PW),))
            d.execute("insert into users(name,email,phone,pw,idcard) values('Andrew','andrew@gmail.com','0911111111',?,'063918304722')", (H('Andrew@123'),))
            for r in [('302-DLX','DLX',100,38,2,'Sea view, private bathroom, vanity table','r1.jpg','S120,S715'),('105-STD','STD',82,20,2,'2 Guests · 1 King Bed · Private Bathroom','r2.jpg','S090'),('401-SUI','SUI',120,50,4,'4 Guests · 2 kingbed · free breakfast','r3.jpg','S120,S090,S715'),('204-SUP','SUP',20,15,2,'2 Guests · 1 kingbed','r4.jpg','')]:
                d.execute('insert into rooms(code,type,price,area,cap,descr,img,svc) values(?,?,?,?,?,?,?,?)', r)
            for s in [('S120','Breakfast',10,'Buffet breakfast'),('S090','Laundry Service',10,'Same-day laundry'),('S715','Airport Shuttle',25,'Airport pick-up'),('S005','Spa',40,'Relaxing spa')]:
                d.execute('insert into services(code,name,price,descr) values(?,?,?,?)', s)
            d.execute("insert into vouchers(code,pct,start,end,cond) values('WELCOME10',30,'2026-01-01','2027-12-31','First booking'),('SAVE20OFF',35,'2026-12-09','2027-01-01','')")
        self.migrate(d); d.commit(); d.close()
    def migrate(self, d):
        """Idempotent upgrade for databases created before RoomType / BookingDetail / Payment / Invoice existed."""
        cols = {r[1] for r in d.execute('pragma table_info(bookings)')}
        for c in ('vat', 'discount'):
            if c not in cols: d.execute(f'alter table bookings add column {c} real default 0')
        if not d.execute('select 1 from roomtypes').fetchone():
            d.executemany('insert into roomtypes(type_id,type_name,description) values(?,?,?)', [('STD', 'Standard', 'Standard room'), ('DLX', 'Deluxe', 'Deluxe room'), ('SUI', 'Suite', 'Suite'), ('SUP', 'Superior', 'Superior room')])
        d.execute("insert or ignore into roomtypes(type_id,type_name,description) select distinct type,type,'' from rooms")
        d.execute("insert into booking_details(detail_id,bcode,rid,nights,room_price,sub_total) select 'D-'||b.code,b.code,b.rid,max(1,cast(julianday(b.cout)-julianday(b.cin) as int)),r.price,r.price*max(1,cast(julianday(b.cout)-julianday(b.cin) as int)) from bookings b join rooms r on r.id=b.rid where not exists(select 1 from booking_details x where x.bcode=b.code)")
        d.execute("insert into payments(payment_id,bcode,amount,method,paid_at,status,refund_amount) select 'P-'||b.code,b.code,b.deposit,coalesce(b.method,'hotel'),b.created,'paid',0 from bookings b where b.paid=1 and not exists(select 1 from payments p where p.bcode=b.code)")
