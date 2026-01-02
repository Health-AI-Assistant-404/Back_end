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
from .models import OTP
from .sms_service import SMSService





class SignupAPI(APIView):
    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Generate OTP
            otp_code = SMSService.generate_otp()

            # Save OTP to database
            OTP.objects.create(
                username=user.username,
                otp_code=otp_code
            )

            # Send OTP via SMS
            success, message = SMSService.send_otp(user.username, otp_code)

            if success:
                return Response({
                    'message': 'OTP sent to your phone number. Please verify to complete registration.',
                    'username': user.username
                }, status=status.HTTP_201_CREATED)
            else:
                # If SMS fails, delete the user and OTP
                user.delete()
                return Response({
                    'error': f'Failed to send OTP: {message}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Your profile edited.', 'data': serializer.data})
        return Response(serializer.errors, status=400)
