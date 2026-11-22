"""Simulated e-mail sender: appends every message to emails.log."""
import datetime as dt
import os

from config import BASE

class Mailer:
    """Simulated e-mail: appends to emails.log (swap for SMTP in production)."""
    def send(self, to, subject, body):
        open(os.path.join(BASE, 'emails.log'), 'a', encoding='utf8').write(f'[{dt.datetime.now():%F %T}] TO {to} | {subject} | {body}\n')
