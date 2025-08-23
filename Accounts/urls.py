
from django.urls import path
from .views import *
urlpatterns = [
    path('verify-otp/',VerifyOTP.as_view()),
    path('get-otp/',Get_otp.as_view()),
    path('reset-password/',Reset_password.as_view()),
    path('signup/',UserCreateView.as_view()),
    path("login/", LoginView.as_view(), name="login"),
    path('user-update/',UserUpdateView.as_view()),
    path("surveys/", SurveyListCreateView.as_view(), name="survey-list-create"),
]
