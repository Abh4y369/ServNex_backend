# from django.urls import path,include
# from rest_framework.routers import DefaultRouter
# from users.views import *

# router= DefaultRouter()
# router.register('register',RegisterViewset,basename='register')

# urlpatterns = [
#     path("login/", LoginView.as_view(), name="login"),
# ]

# urlpatterns += router.urls

from django.urls import path
from rest_framework.routers import DefaultRouter
from users.views import (
    SendOTPView,
    VerifyOTPView,
    ResetPasswordView,
    RegisterViewset,
    LoginView,
    UpdateRoleView,
    BusinessProfileView,
    UserProfileUpdateView,
    UserDeleteView,
)

router = DefaultRouter()
router.register('register', RegisterViewset, basename='register')

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),

    # Forgot Password OTP
    path("forgot-password/send-otp/", SendOTPView.as_view()),
    path("forgot-password/verify-otp/", VerifyOTPView.as_view()),
    path("forgot-password/reset-password/", ResetPasswordView.as_view()),
    path("update-role/", UpdateRoleView.as_view(),name="update-role"),
    path("update-profile/", UserProfileUpdateView.as_view(), name="update-profile"),
    path("delete-profile/", UserDeleteView.as_view(), name="delete-profile"),
    path("api/business-profile/", BusinessProfileView.as_view(), name="business-profile"),
]

urlpatterns += router.urls
