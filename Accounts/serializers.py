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