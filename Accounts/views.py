from .utils import *
from .models import *
from .serializers import *
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken, TokenError

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
            isvalid = verify_otp(email, otp_code)
            if not isvalid:
                return Response(
                    {"success": False, "error": "Invalid OTP or OTP has expired."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user = User.objects.get(email=email)
            user.is_active = True
            user.save()
            return Response(
                {"success": True, "message": "OTP verified successfully."},
                status=status.HTTP_200_OK
            )
        except OTP.DoesNotExist:
            return Response(
                {"success": False, "error": "Invalid OTP or email."},
                status=status.HTTP_400_BAD_REQUEST
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
        success = send_otp(email, task)

        if success:
            return Response(
                {"success": True, "message": f"OTP sent successfully for {task or 'Verification'}."},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
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
            access_token = request.data.get("access")

            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()  # destroys refresh token

            if access_token:
                token = AccessToken(access_token)
                token.blacklist()  # optional: destroys access token immediately

            return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)

        except TokenError:
            return Response({"detail": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({"detail": "Something went wrong."}, status=status.HTTP_400_BAD_REQUEST)