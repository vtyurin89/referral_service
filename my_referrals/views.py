from django.contrib.auth.models import update_last_login
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserSerializer, UserLoginSerializer, ReferralCodeSerializer
from .models import *


class UserRegisterView(APIView):
    def post(self, request):
        data = JSONParser().parse(request)
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        update_last_login(None, user)
        refresh = RefreshToken.for_user(user)
        return Response({
            "status": status.HTTP_200_OK,
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh)
        })


class ReferralView(APIView):
    permission_classes = [IsAuthenticated]

    def get_code_object(self, request):
        try:
            return ReferralCode.objects.get(user=request.user)
        except ReferralCode.DoesNotExist:
            raise NotFound("Referral code not found")

    def get(self, request):
        code = self.get_code_object(request)
        serializer = ReferralCodeSerializer(code)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create_or_update_code(self, request):
        code = self.get_code_object(request)
        if code:
            code.delete()
        new_code = ReferralCode.objects.create(user=request.user)
        return new_code

    def post(self, request):
        new_code = self.create_or_update_code(request)
        serializer = ReferralCodeSerializer(new_code, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request):
        code = self.get_code_object(request)
        code.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReferralCodeByUserEmailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_code_object(self, email):
        try:
            return ReferralCode.objects.get(user__email=email)
        except ReferralCode.DoesNotExist:
            raise NotFound("Referral code not found.")

    def get(self, request):
        email = request.query_params.get('email')
        if not email:
            return Response({"error": "Email address is required."}, status=status.HTTP_400_BAD_REQUEST)

        referral_code = self.get_code_object(email)
        if not referral_code:
            return Response({"error": "Referral code not found for the given email."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ReferralCodeSerializer(referral_code)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReferralListView(APIView):
    permission_classes = [IsAuthenticated]

    def get_referrer_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise NotFound("User not found.")

    def get(self, request, pk):
        referrer = self.get_referrer_object(pk)
        referrals = User.objects.filter(referrer=referrer)
        serializer = UserSerializer(referrals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)