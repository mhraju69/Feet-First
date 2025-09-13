
from django.urls import path
from .views import *
urlpatterns = [ 
    path('',ProductListView.as_view()),
    path('<int:id>/',ProductDetailView.as_view()),
    path("footscans/", FootScanListCreateView.as_view(), name="foot_scan_list_create"),
    path('footscan/<int:scan_id>/download/', DownloadFootScanExcel.as_view(), name='download_foot_scan'),
]
