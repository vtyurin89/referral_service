from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework.serializers import ModelSerializer, Serializer, CharField
from datetime import datetime

from .models import *


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        referrer = None

        # checking referral code
        if validated_data.get('referral_code', None):
            referral_code = validated_data.pop('referral_code')
            try:
                check_code = ReferralCode.objects.get(code=referral_code)
                if check_code.expiration_date > datetime.now():
                    referrer = check_code.user
            except ObjectDoesNotExist:
                pass

        user = User.objects.create(**validated_data)
        user.set_password(password)
        if referrer:
            user.referrer = referrer

        user.save()
        return user


class UserLoginSerializer(Serializer):
    username = CharField(max_length=255)
    password = CharField()

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(request=self.context.get('request'),
                                username=username, password=password)
            if not user:
                raise ValidationError("Unable to log in with provided credentials!", code=401)
        else:
            raise ValidationError("Please provide both username and password!", code=401)
        data['user'] = user
        return data


class ReferralCodeSerializer(ModelSerializer):
    class Meta:
        model = ReferralCode
        fields = ['user', 'code', 'expiration_date']
