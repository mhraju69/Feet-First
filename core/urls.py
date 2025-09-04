from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from Contact.views import ContactListView
from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView,)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('Accounts.urls')),
    path('api/products/', include('Products.urls')),
    path('api/surveys/', include('Surveys.urls')),
    path("accounts/", include("django.contrib.auth.urls")),  
    path('api/contactus/',ContactListView.as_view(),name='contactus'),
    path('', RedirectView.as_view(url='/admin/', permanent=False)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
] 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
