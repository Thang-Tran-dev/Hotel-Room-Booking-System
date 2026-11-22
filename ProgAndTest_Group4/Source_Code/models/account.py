"""Account entity + UserRepo (users table)."""
from config import Config
from flask import session
from models.base import Entity, Repository

class Account(Entity):
    FIELDS = {'account_id': 'id', 'full_name': 'name', 'email': 'email', 'password': 'pw', 'phone_number': 'phone'}
    def logout(self): session.clear()
    def reset_password(self, email): self.ctx.auth.forgot(email); return True
    def change_password(self, old_password, new_password, confirm=None):
        self.ctx.auth.change_password(self.ctx.users.get(self.account_id), {'old': old_password, 'new': new_password, 'new2': new_password if confirm is None else confirm}); return True
    def validate_password(self, password): return bool(Config.PW.match(password or ''))
    def send_notice(self, content): self.ctx.mail.send(self.email, 'Notice', content)

class UserRepo(Repository):
    table, key = 'users', 'id'
    @staticmethod
    def public(u): return {k: u[k] for k in ('id', 'name', 'email', 'phone', 'role', 'idcard', 'address', 'dob', 'sex', 'locked')}
    def by_email(self, e): return self.get(e, 'email')
    def customers(self): return self.db.q("select * from users where role='customer'")
    def toggle_lock(self, i): self.db.q("update users set locked=1-locked,fails=0 where id=? and role='customer'", (i,))
