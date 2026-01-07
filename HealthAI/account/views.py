from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from .serializers import (
    UserSignupSerializer,
    VerifyOTPSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAdminUser
from django.contrib.auth.models import User
from .serializers import UserProfileSerializer
from rest_framework.generics import ListAPIView
from django.contrib.auth.models import User
from .serializers import UserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import UserProfile
from .serializers import UserProfileSerializer
from .models import OTP
from .sms_service import SMSService
from rest_framework import status
from django.contrib.auth.models import User
from .serializers import UserSignupSerializer
from .models import OTP, UserProfile
from .serializers import UserProfileSerializer
from rest_framework.permissions import IsAuthenticated

# سرویس فرضی برای ارسال OTP
class SMSService:
    @staticmethod
    def generate_otp():
        import random
        return str(random.randint(100000, 999999))

    @staticmethod
    def send_otp(username, otp_code):
        # اینجا باید سرویس واقعی SMS وصل بشه
        print(f"Send OTP {otp_code} to {username}")
        return True, "OTP sent"

class SignupAPI(APIView):
    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "Sign up is successful", "username": user.username}, status=201)
        return Response(serializer.errors, status=400)


class VerifyOTPAPI(APIView):
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            otp_instance = serializer.validated_data['otp_instance']

            try:
                user = User.objects.get(username=username)

                # Activate the user
                user.is_active = True
                user.save()

                # Mark OTP as used
                otp_instance.is_used = True
                otp_instance.save()

                return Response({
                    'message': 'Account activated successfully. You can now login.',
                    'username': user.username
                }, status=status.HTTP_200_OK)

            except User.DoesNotExist:
                return Response({
                    'error': 'User not found.'
                }, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordAPI(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']

            # Generate OTP
            otp_code = SMSService.generate_otp()

            # Save OTP to database
            OTP.objects.create(
                username=username,
                otp_code=otp_code
            )

            # Send OTP via SMS
            success, message = SMSService.send_otp(username, otp_code)

            if success:
                return Response({
                    'message': 'OTP sent to your phone number. Please use it to reset your password.',
                    'username': username
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': f'Failed to send OTP: {message}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordAPI(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user_instance']
            otp_instance = serializer.validated_data['otp_instance']
            new_password = serializer.validated_data['new_password']

            # Update user password
            user.set_password(new_password)
            user.save()

            # Mark OTP as used
            otp_instance.is_used = True
            otp_instance.save()

            return Response({
                'message': 'Password reset successfully. You can now login with your new password.',
                'username': user.username
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPI(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            return Response({'message': 'login successful'}, status=status.HTTP_200_OK)
        return Response({'error': 'The username or password is incorrect.'}, status=status.HTTP_401_UNAUTHORIZED)


class UserDashboard(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'username': user.username,
            'email': user.email,
            'message': f'Wellcome{user.username}!'
        })



class UserListView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]   # فقط ادمین‌ها اجازه دارن



class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'اطلاعات پروفایل به‌روزرسانی شد', 'data': serializer.data})
        return Response(serializer.errors, status=400)
