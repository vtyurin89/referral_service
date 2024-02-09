from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="Referral Code API",
      default_version='v1',
      description="The API allows users to generate and delete referral codes, register new users using referral codes, "
                  "get the list of referrals of each referrer, get referral code using the referrer's email.",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="vlad89main@gmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('admin/', admin.site.urls),
    path('', include('my_referrals.urls')),
]
