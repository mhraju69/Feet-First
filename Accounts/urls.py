
from django.urls import path
from .views import *
urlpatterns = [
    path('get-otp/',GetOtp.as_view(), name="get_otp"),
    path('verify-otp/',VerifyOTP.as_view(), name="verify_otp"),
    path('signup/',UserCreateView.as_view(), name="signup"),
    path('reset-password/',ResetPassword.as_view()),
    path('user-update/',UserUpdateView.as_view()),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("surveys/", SurveyListCreateView.as_view(), name="survey-list-create"),
    path("addresses/", AddressListCreateView.as_view(), name="address-list-create"),
    path("addresses/<int:pk>/", AddressDetailView.as_view(), name="address-detail"),
]
