from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.core.validators import validate_email
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError, AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken


from .serializers import UserSerializer, ReferralCodeSerializer
from .models import *


class UserRegisterView(APIView):
    """
    Takes new user's username, password and (optionally) email and referral code
    and creates a new user object.
    """
    def post(self, request):
        data = request.data

        username = data.get('username')

        if User.objects.filter(username=username).exists():
            return Response({"error": "User with this username already exists!"},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = UserSerializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    """
    Takes user's username and password and returns JWT access token and refresh token.
    """
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request=request, username=username, password=password)
        if user:
            update_last_login(None, user)
            refresh = RefreshToken.for_user(user)
            return Response({
                "status": status.HTTP_200_OK,
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh)
            })
        else:
            raise AuthenticationFailed("Unable to log in with provided credentials!", code=401)


class ReferralCodeView(APIView):
    """
    Requires user's JWT access token.
    GET request: returns user's referral code.
    POST request: creates a new referral code (deletes old one if it existed).
    DELETE request: deletes user's referral code.
    """
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
        try:
            code = self.get_code_object(request)
            if code:
                code.delete()
        except NotFound:
            pass
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


class ReferralCodeByEmailView(APIView):
    """
    Requires user's JWT access token.
    GET request: returns referral code of the user whose email was in the URL
    (if the user has it).
    """
    permission_classes = [IsAuthenticated]

    def get_object(self, email):
        try:
            return ReferralCode.objects.get(user__email=email)
        except ReferralCode.DoesNotExist:
            return None

    def get(self, request, email):
        if not email:
            return Response({"error": "Email address is required!"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            validate_email(email)
        except ValidationError:
            return Response({"error": "Invalid email address!"}, status=status.HTTP_400_BAD_REQUEST)

        referral_code = self.get_object(email)
        if not referral_code:
            return Response({"error": "Referral code not found for the given email!"}, status=status.HTTP_404_NOT_FOUND)
        if referral_code.expiration_date < timezone.now():
            return Response({"error": "This user's referral code has expired!"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ReferralCodeSerializer(referral_code)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserReferralListView(APIView):
    """
    Requires user's JWT access token.
    GET request: takes pk from the url and returns a list of referrals of corresponding user.
    """
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise NotFound("User not found.")

    def get(self, request, pk, format=None):
        referrer = self.get_object(pk)
        referrals = User.objects.filter(referrer=referrer)
        serializer = UserSerializer(referrals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)