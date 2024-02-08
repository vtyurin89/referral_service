import uuid
from datetime import timedelta
from django.utils import timezone


from .constants import REFERRAL_CODE_EXPIRATION_IN_DAYS


def get_code_expiration_time():
    return timezone.now() + timedelta(days=REFERRAL_CODE_EXPIRATION_IN_DAYS)


def generate_code():
    return str(uuid.uuid4().hex)