"""Customer operations about the profile."""
from models.account import UserRepo

class CustomerAccount:
    """view_profile, update_profile"""
    def view_profile(self): return UserRepo.public(self.ctx.users.get(self.customer_id))
    def update_profile(self, full_name, phone_number, identity_card, address, sex, date_of_birth):
        return UserRepo.public(self.ctx.auth.update_profile(self.user, dict(name=full_name, phone=phone_number, idcard=identity_card, address=address, sex=sex, dob=date_of_birth)))
