from django.shortcuts import render
import requests
from .utils import *
from .models import *
from .serializers import *
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password

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

class VerifyOTP(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp_code = request.data.get('otp_code')

        if not email or not otp_code:
            return Response(
                {"error": "Email and OTP code are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = verify_otp(email, otp_code)

        if result['success']:
            return Response({"success": True, "message": result['message']}, status=status.HTTP_200_OK)
        else:
            # 403 for lock, 400 for invalid/expired
            status_code = status.HTTP_403_FORBIDDEN if "Too many attempts" in result['message'] else status.HTTP_400_BAD_REQUEST
            return Response({"success": False, "error": result['message']}, status=status_code)

class ResetPassword(APIView):
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
            result = verify_otp(email, otp_code)
            if not result['success']:
                return Response({"error": result['message']}, status=400)

        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            return Response({"success": True, "message": "Password reset successfully"}, status=200)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

class GetOtp(APIView):
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
        
class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user   # not used but keeps UpdateAPIView contract

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Password updated successfully."}, status=status.HTTP_200_OK)

def login(request):
        return render(request, "google.html",{
            'google_client_id': settings.GOOGLE_OAUTH_CLIENT_ID,
            'google_callback_uri': settings.GOOGLE_OAUTH_CALLBACK_URL,
        })

class SocialAuthCallbackView(APIView):
    def get(self, request):
        code = request.GET["code"]  
        if not code:
            return Response({"error": "No code provided"}, status=400)

        # Step 1: Exchange code for access_token
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
            "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_OAUTH_CALLBACK_URL,
            "grant_type": "authorization_code",
        }

        token_res = requests.post(token_url, data=data)
        if token_res.status_code != 200:
            return Response({"error": "Failed to get token"}, status=400)

        token_json = token_res.json()
        access_token = token_json.get("access_token")

        # Step 2: Get user info from Google
        userinfo_res = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        if userinfo_res.status_code != 200:
            return Response({"error": "Failed to fetch user info"}, status=400)

        user_info = userinfo_res.json()
        email = user_info.get("email")
        name = user_info.get("name")
        profile_image = user_info.get("picture")

        # সমাধান: সঠিকভাবে get_or_create ব্যবহার
        user, created = User.objects.get_or_create(
            email=email,  # ইউনিক ফিল্ড হিসেবে email ব্যবহার
            defaults={
                'name': name,
                'password': make_password(None),
                'is_active': True,
                'image': profile_image

            }
        )
        # if created:
        #     User.objects.create(user=user)
        refresh = RefreshToken.for_user(user)
        return Response({
            "email": email,
            "name": name,
            "image": profile_image, 
            "hasSubmitted": True,
            'isNewUser': True if created else False, 
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }, status=status.HTTP_201_CREATED)