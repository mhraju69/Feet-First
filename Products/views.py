from .models import *
from .serializers import *
from rest_framework import permissions
from rest_framework import generics,views
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
# Create your views here.

class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [OrderingFilter]
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)
        main = self.request.query_params.get("main_category")
        sub = self.request.query_params.get("sub_category")

        if main and sub:
            # OR condition
            queryset = queryset.filter(Q(main_category=main) | Q(sub_category=sub))
        elif main:
            queryset = queryset.filter(main_category=main)
        elif sub:
            queryset = queryset.filter(sub_category=sub)

        return queryset

class ProductDetailView(generics.RetrieveAPIView):
    serializer_class = ProductDetailsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Product.objects.filter(is_active = True)
    lookup_field = 'id'

class ProductMatchView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # get latest FootScan for current user
        try:
            scan = FootScan.objects.filter(user=request.user).latest("created_at")
        except FootScan.DoesNotExist:
            return Response({"error": "No FootScan found for this user"}, status=404)

        # fetch all products
        products = Product.objects.filter(is_active=True)

        # serialize with scan in context (so we can calculate % match)
        serializer = ProductMatchSerializer(products, many=True, context={"scan": scan})

        # sort by best match %
        sorted_data = sorted(
            serializer.data,
            key=lambda x: x["match_percentage"] if x["match_percentage"] else 0,
            reverse=True,
        )

        return Response(sorted_data)