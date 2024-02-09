from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.serializers import ModelSerializer
from django.utils import timezone
from rest_framework.serializers import CharField

from .models import *


class UserSerializer(ModelSerializer):
    referral_code = CharField(max_length=255, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'password', "email", "referral_code"]
        extra_kwargs = {'email': {'write_only': True}, 'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        referral_code = validated_data.pop('referral_code', None)
        email = validated_data.pop('email', None)
        referrer = None

        if referral_code:
            try:
                check_code = ReferralCode.objects.get(code=referral_code)
                if check_code.expiration_date > timezone.now():
                    referrer = check_code.user
                else:
                    raise ValidationError("Referral code has expired", code=status.HTTP_400_BAD_REQUEST)
            except ReferralCode.DoesNotExist:
                raise ValidationError("This referral code does not exist", code=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(**validated_data, password=password, email=email)
        if referrer:
            user.referrer = referrer
            user.save()

        return user


class ReferralCodeSerializer(ModelSerializer):
    class Meta:
        model = ReferralCode
        fields = ['user', 'code', 'expiration_date']
