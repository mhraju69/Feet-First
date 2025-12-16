from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from Contact.views import ContactListView
from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView,)
from Others.views import *
from Products.admin import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('Accounts.urls')),
    path('api/products/', include('Products.urls')),
    path('api/surveys/', include('Surveys.urls')),
    path("accounts/", include("django.contrib.auth.urls")),  
    path('api/brands/', include('Brands.urls')), 
    path('', RedirectView.as_view(url='/admin/', permanent=False)),
    path('api/contactus/',ContactListView.as_view(),name='contactus'),
    path('answer-autocomplete/', AnswerAutocomplete.as_view(), name='answer-autocomplete'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/faq/', FAQAPIView.as_view(), name='faq-list'),
    path('api/news/', NewsAPIView.as_view(), name='news-list'),
    path('subcategory-autocomplete/',SubCategoryAutocomplete.as_view(),name='subcategory-autocomplete',),
    path('api/create-order/', CreateOrderView.as_view(), name='create-order'),
    path('api/dashboard/', DashboardAPIView.as_view(), name='dashboard'),
    path('api/orders/', OrderPageAPIView.as_view(), name='order-page'),
    path('api/orders/info/', OrderAnalyticsAPIView.as_view(), name='order-info'),
    path('api/warehouse/', WarehouseAPIView.as_view(), name='warehouse'),
    path('api/warehouse/<int:pk>/', WarehouseUpdateDestroyAPIView.as_view(), name='warehouse-update'),
    path('api/stripe-webhook/', stripe_webhook.as_view(), name='stripe-webhook'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
