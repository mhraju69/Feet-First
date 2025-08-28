from .models import *
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
User = get_user_model()
from .utils import send_otp


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        send_otp(user.email)  
        return user       

class UserUpdateSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ['name', 'email', 'password', 'image']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}
        }

    def update(self, instance, validated_data):
        # password set properly if provided
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            raise serializers.ValidationError("Both email and password are required.")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password.")

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid email or password.")
        if not user.is_active:
            raise serializers.ValidationError("Your account is inactive.Please contact support.")

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return {
            "user": UserSerializer(user).data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }  
    
class SurveySerializer(serializers.ModelSerializer):
    # POST/PUT এর জন্য list হিসেবে source field
    source = serializers.ListField(
        child=serializers.ChoiceField(choices=OnboardingSurvey.SOURCE_CHOICES),
        write_only=True
    )
    # GET এর জন্য list হিসেবে দেখাবে
    source_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = OnboardingSurvey
        fields = [
            'id', 'source', 'source_display', 'product_preference',
            'foot_problems', 'created_at', 'user'
        ]
        read_only_fields = ['id', 'created_at', 'user', 'source_display']

    def get_source_display(self, obj):
        if obj.source:
            return obj.source.split(',')
        return []

    def create(self, validated_data):
        user = self.context['request'].user

        # Duplicate survey check
        if OnboardingSurvey.objects.filter(user=user).exists():
            raise serializers.ValidationError("You have already submitted the survey.")

        # Convert list to comma-separated string
        source_list = validated_data.pop('source', [])
        validated_data['source'] = ','.join(source_list)

        # Attach user
        validated_data['user'] = user

        return super().create(validated_data)

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'
        read_only_fields = ["id", "created_at", "updated_at", "user"]

class ChangePasswordSerializer(serializers.Serializer):
    old_pass = serializers.CharField(write_only=True)
    new_pass1 = serializers.CharField(write_only=True)
    new_pass2 = serializers.CharField(write_only=True)

    def validate(self, data):
        user = self.context['request'].user
        if not user.check_password(data['old_pass']):
            raise serializers.ValidationError({"old_pass": "Incorrect password"})
        if data['new_pass1'] != data['new_pass2']:
            raise serializers.ValidationError({"new_pass2": "Passwords doesn't match"})
        return data

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_pass1'])
        user.save()
        return user