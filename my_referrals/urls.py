from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

from .views import *

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/v1/register/', UserRegisterView.as_view(), name="register"),
    path('api/v1/login/', UserLoginView.as_view(), name="login"),
    path('api/v1/ref_code/', ReferralCodeView.as_view(), name="referral_code_use"),
    path('api/v1/ref_code_by_email/<str:email>/', ReferralCodeByEmailView.as_view(), name="referral_code_get_by_email"),
    path('api/v1/referrals/<str:pk>/', UserReferralListView.as_view(), name="check_referrals_by_id"),
]

