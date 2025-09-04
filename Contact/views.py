from .serializers import ContactSerializer
from rest_framework import generics, permissions
from .models import ContactUs
# Create your views here.

class ContactListView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ContactSerializer
    queryset = ContactUs.objects.all()

    
