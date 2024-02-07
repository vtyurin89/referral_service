from django.urls import path

from .views import *

urlpatterns = [
    path('api/v1/register/', UserRegisterView.as_view()),
    path('api/v1/login/', UserLoginView.as_view()),

]