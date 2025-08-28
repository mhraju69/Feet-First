from .utils import *
from .models import *
from .serializers import *
from datetime import timedelta
from django.utils import timezone
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken

# Create your views here.

class UserCreateView(generics.CreateAPIView):
    serializer_class = UserSerializer

class UserUpdateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
    
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SurveyListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = OnboardingSurvey.objects.all()
    serializer_class = SurveySerializer

class VerifyOTP(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp_code = request.data.get('otp_code')

        if not email or not otp_code:
            return Response(
                {"error": "Email and OTP code are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            otp_obj = OTP.objects.filter(user__email=email).latest('created_at')
        except OTP.DoesNotExist:
            return Response(
                {"success": False, "error": "Invalid OTP or email."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if OTP is expired
        if otp_obj.is_expired():
            return Response(
                {"success": False, "error": "OTP has expired."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if user can try
        if otp_obj.attempt_count >= 3:
            # Lock for 1 minute
            if otp_obj.last_tried and otp_obj.last_tried + timedelta(minutes=1) > timezone.now():
                remaining = int((otp_obj.last_tried + timedelta(minutes=1) - timezone.now()).seconds)
                return Response(
                    {"success": False, "error": f"Too many attempts. Try again in {remaining} seconds."},
                    status=status.HTTP_403_FORBIDDEN
                )
            else:
                otp_obj.attempt_count = 0  # reset after 1 min

        # Verify OTP
        if not verify_otp(email, otp_code):
            otp_obj.attempt_count += 1
            otp_obj.last_tried = timezone.now()
            otp_obj.save()
            return Response(
                {"success": False, "error": f"Invalid OTP. You have {3 - otp_obj.attempt_count} attempts left."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # OTP verified successfully
        user = otp_obj.user
        user.is_active = True
        user.save()

        # Delete OTP after success
        otp_obj.delete()

        return Response(
            {"success": True, "message": "OTP verified successfully."},
            status=status.HTTP_200_OK
        )

class Reset_password(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):   
        email = request.data.get('email')
        otp_code = request.data.get('otp_code')
        new_password = request.data.get('new_password')

        if not email or not new_password:
            return Response(
                {"error": "Email and new password are required."},
                status=400
            )

       
        if otp_code:
            if not verify_otp(email, otp_code):  
                return Response({"error": "Invalid OTP"}, status=400)

        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            return Response({"success": True}, status=200)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

class Get_otp(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        task = request.data.get('task', '')
        if not email:
            return Response(
                {"error": "Email is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        res = send_otp(email, task)

        if res['success']:
            return Response({"success": True, "message": res['message']}, status=status.HTTP_200_OK)
        else:
            return Response({"error": res['message']}, status=status.HTTP_400_BAD_REQUEST)
        
class AddressListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AddressSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AddressSerializer
    queryset = Address.objects.all()

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()    
            return Response({"message": "Logged out successfully"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
        

