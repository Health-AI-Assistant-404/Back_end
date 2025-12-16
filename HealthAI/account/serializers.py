from rest_framework import serializers
from django.contrib.auth.models import User
from .models import OTP


class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This phone number is already registered.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password'],
            is_active=False
        )
        return user



class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']
        read_only_fields = ['username']  



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff', 'is_superuser']


class VerifyOTPSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    otp_code = serializers.CharField(max_length=6)

    def validate(self, data):
        username = data.get('username')
        otp_code = data.get('otp_code')

        try:
            otp = OTP.objects.filter(
                username=username,
                otp_code=otp_code,
                is_used=False
            ).latest('created_at')

            if not otp.is_valid():
                raise serializers.ValidationError("OTP has expired or is invalid.")

            data['otp_instance'] = otp
        except OTP.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP code.")

        return data

