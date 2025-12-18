
from django.urls import path
from .views import *
urlpatterns = [ 
    path('',BrandListView.as_view()),
]
