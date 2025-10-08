import requests
from .utils import *
from .models import *
from .serializers import *
from rest_framework import generics
from django.utils.text import slugify
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.files.base import ContentFile
from rest_framework.exceptions import NotFound
from rest_framework_simplejwt.exceptions import TokenError 
from rest_framework import status, permissions
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken,AccessToken

# Create your views here.

class UserCreateView(generics.CreateAPIView):
    serializer_class = UserSerializer

class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return User.objects.filter(email=self.request.user.email)

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
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                "user": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        else:
            # 403 for lock, 400 for invalid/expired
            status_code = status.HTTP_403_FORBIDDEN if "Too many attempts" in result['message'] else status.HTTP_400_BAD_REQUEST
            return Response({"success": False, "error": result['message']}, status=status_code)

class ResetPassword(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        email = request.data.get('email')
        new_password = request.data.get('new_password')

        if not email or not new_password :
            return Response(
                {"error": "Email and new password are required."},
                status=400
            )
        
        elif request.user.email != email :
            return Response(
                {"error": "You can only reset your own password."},
                status=403)
        
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
        return Address.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        addr = Address.objects.filter(user=self.request.user).first()
        if addr:
            raise serializers.ValidationError({"error":"Address already exists. You can update or delete it."})
        serializer.save(user=self.request.user)

class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AddressSerializer
    queryset = Address.objects.all()

    def get_object(self):
        user = self.request.user

        try:
            address = Address.objects.get(user=user)
        except Address.DoesNotExist:
            raise NotFound({"error":"Address not found"})
        return address

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

class DeleteRequestView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DeleteSerializer
    # queryset = AccountDeletionRequest.objects.all()

    def perform_create(self, serializer):
        serializer.save(email=self.request.user.email)

class SocialAuthCallbackView(APIView):
    def post(self, request):
        access_token = request.data.get('access_token')
        
        if not access_token:
            return Response({'error': 'No access token provided'}, status=400)
        print("Access Token:", access_token)
        try:
            # Token verify করুন
            token_info_response = requests.get(
                f'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}'
            )
            
            if token_info_response.status_code != 200:
                return Response({'error': 'Invalid access token'}, status=400)
            
            token_info = token_info_response.json()
            
            # Check if token is valid for your app
            if 'error' in token_info:
                return Response({'error': token_info['error']}, status=400)
            
            # Get user info
            user_info_response = requests.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            
            user_data = user_info_response.json()
            profile_image_url = user_data.get("picture")
            email = user_data.get("email")
            name = user_data.get("name")
            
            print(user_data)
            
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'name': name,
                    'is_active': True,
                    'password': make_password(None)  # unusable password
                }
            )
            
            if created and user_data.get("picture"):
                img_response = requests.get(profile_image_url)
                if img_response.status_code == 200:
                    file_name = f"{slugify(name)}-profile.jpg"
                    user.image.save(file_name, ContentFile(img_response.content), save=True)

            # Generate tokens
            if user.suspend:   
                return Response({"error": "User account is disabled.Please contact to support"}, status=403)
            
            refresh = RefreshToken.for_user(user)
            serializers = UserSerializer(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': serializers.data,
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=500)
        
class VerifyAccessView(APIView):
    def post(self, request):
        access_token = request.data.get("access_token")
        refresh_token = request.data.get("refresh_token")

        if not access_token:
            return Response({"success": False, "message": "Access token required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = AccessToken(access_token)
            user = User.objects.get(id=token['user_id'])
            user_data = UserSerializer(user).data
            return Response({"success": True, "access": access_token, "user": user_data})
        except TokenError:
            if not refresh_token:
                return Response({"success": False, "message": "Access token expired, no refresh token provided"}, status=status.HTTP_401_UNAUTHORIZED)
            try:
                refresh = RefreshToken(refresh_token)
                new_access = str(refresh.access_token)
                # Get user from refresh token
                user = User.objects.get(id=refresh['user_id'])
                user_data = UserSerializer(user).data
                return Response({"success": True, "access": new_access, 'refresh': refresh_token, "user": user_data})
            except TokenError:
                return Response({"success": False, "message": "Refresh token expired or invalid"}, status=status.HTTP_401_UNAUTHORIZED)

class PartnerView(generics.ListAPIView):
    queryset = User.objects.filter(role = 'partner')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]