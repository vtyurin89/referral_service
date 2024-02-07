import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

from .utils import get_code_expiration_time, generate_code


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    referrer = models.ForeignKey('self', null=True, related_name='referrals', on_delete=models.SET_NULL)

    def __str__(self):
        return self.username


class ReferralCode(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE)
    code = models.CharField(unique=True, max_length=200)
    expiration_date = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.expiration_date = get_code_expiration_time()
            self.code = generate_code()
        super().save(*args, **kwargs)

