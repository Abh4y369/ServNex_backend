from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from .models import PasswordResetOTP

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'email', 'password', 'phone','role')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        # Map frontend account_type to backend role
        account_type = self.initial_data.get('account_type')
        role = validated_data.get('role') or 'User'
        
        if account_type == 'business':
            role = 'Business'
            
        user = User.objects.create_user(
            first_name=validated_data.get('first_name'),
            email=validated_data.get('email'),
            password=validated_data.get('password'),
            phone=validated_data.get('phone'),
            role=role
        )
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'email', 'phone', 'profile_image')
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            raise serializers.ValidationError("Email and password are required")

        user = authenticate(
            request=self.context.get('request'),
            username=email,   # CustomUser uses email as USERNAME_FIELD
            password=password
        )

        if not user:
            raise serializers.ValidationError("Invalid email or password")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled")

        data['user'] = user
        return data




class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist")
        return value


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6)
    confirm_password = serializers.CharField(min_length=6)

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match")
        return data

class UserRoleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['role']