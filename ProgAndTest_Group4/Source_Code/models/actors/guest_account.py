"""Guest operations about accounts: sign up / sign in."""

class GuestAccount:
    """sign_up, sign_in"""
    def sign_up(self, full_name, password, email, phone_number, confirm=None):
        self.ctx.auth.register(dict(name=full_name, pw=password, pw2=password if confirm is None else confirm, email=email, phone=phone_number)); return True
    def sign_in(self, email, password, remember=False):
        row = self.ctx.auth.login(dict(email=email, pw=password, remember=remember))
        from models.actors import Admin, Customer          # imported here to avoid a circular import
        return Admin(self.ctx, row) if row['role'] == 'admin' else Customer(self.ctx, row)
