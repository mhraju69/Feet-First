
from django.urls import path
from .views import *
# from .admin import AnswerAutocomplete
urlpatterns = [ 
    path('',ProductListView.as_view()),
    path('<int:id>/',ProductDetailView.as_view()),
    path("count/", ProductsCountView.as_view(), name="products_count"),
    path('favorites/', FavoriteUpdateView.as_view(), name='favorite-add-remove'),
    path("footscans/", FootScanListCreateView.as_view(), name="foot_scan_list_create"),
    path('qna-match/', ProductQnAFilterAPIView.as_view(), name='answer-autocomplete'),
    path('suggestions/<int:product_id>/', SuggestedProductsView.as_view(), name='product_suggestions'),
    path('all/', AllProductsForPartnerView.as_view(), name='approved_partner_product_update'),
    path('partner/', ApprovedPartnerProductView.as_view(), name='approved_partner_product_update'),
    path('partner/<int:product_id>/', SingleProductForPartnerView.as_view(), name='partner_product_detail'),
    path('partner/<int:product_id>/<str:action>/', ApprovedPartnerProductUpdateView.as_view(), name='approved_partner_product_update'),
]
