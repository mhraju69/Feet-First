
from django.urls import path
from .views import *
urlpatterns = [
    path("onboarding-surveys/", SurveyListCreateView.as_view(), name="survey-list-create"),
    path("onboarding-surveys/me/", SurveyRetrieveUpdateDestroyView.as_view(), name="survey-retrieve"),
]
