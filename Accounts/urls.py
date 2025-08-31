
from django.urls import path
from .views import *
urlpatterns = [
    path('user-update/',UserUpdateView.as_view()),
    path('reset-password/',ResetPassword.as_view()),
    path('get-otp/',GetOtp.as_view(), name="get_otp"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path('signup/',UserCreateView.as_view(), name="signup"),
    path('verify-otp/',VerifyOTP.as_view(), name="verify_otp"),
    path("google/callback/", SocialAuthCallbackView.as_view()),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("addresses/", AddressListCreateView.as_view(), name="address-list-create"),
    path("addresses/<int:pk>/", AddressDetailView.as_view(), name="address-detail"),
    path("google/", login, name="user-profile"),
]
