
from django.urls import path
from .views import *
urlpatterns = [ 
    # path('categories/',CategoryListView.as_view()),
    # path('subcategories/',SubcategoryListView.as_view()),
    path('',ProductListView.as_view()),
    path('<int:id>/',ProductDetailView.as_view()),
    path("match/", ProductMatchView.as_view(), name="product-match"),
]
