from rest_framework import viewsets, permissions, status, parsers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings  # ← Add this import
from rest_framework_simplejwt.tokens import RefreshToken
import random

from .models import PasswordResetOTP
from .serializers import (
    SendOTPSerializer,
    VerifyOTPSerializer,
    ResetPasswordSerializer,
    RegisterSerializer,
    LoginSerializer,
    UserRoleUpdateSerializer,
    UserUpdateSerializer,
)

User = get_user_model()

class RegisterViewset(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def create(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user_obj = serializer.save()
            refresh = RefreshToken.for_user(user_obj)
            return Response(
                {
                    "message": "User registered successfully",
                    "user": serializer.data,
                    "access": str(refresh.access_token),
                    "refresh": str(refresh)
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            user = serializer.validated_data["user"]
            refresh = RefreshToken.for_user(user)

            return Response({
                "message": "Login successful",
                "user": {
                    "id": user.id,
                    "first_name": user.first_name,
                    "email": user.email,
                    "phone": user.phone,
                    "role": getattr(user, "role", None),
                    "profile_image": user.profile_image.url if user.profile_image else None,
                },
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendOTPView(APIView):
    permission_classes = [AllowAny]  # ← Add this
    
    def post(self, request):
        print(f"📨 Received request data: {request.data}")  # Debug log
        
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        user = User.objects.get(email=email)
        otp = str(random.randint(100000, 999999))

        # Save OTP to database
        PasswordResetOTP.objects.create(user=user, otp=otp)
        print(f"💾 OTP saved to database: {otp} for {email}")  # Debug log

        # Send email
        try:
            send_mail(
                subject="Password Reset OTP",
                message=f"Your OTP is {otp}. It is valid for 10 minutes.",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],  # Send to the user's email
                fail_silently=False,
            )
            print(f"✅ Email sent successfully to {email} with OTP: {otp}")  # Debug log
            return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)
        
        except Exception as e:
            print(f"❌ Email sending failed: {str(e)}")  # Debug log
            return Response(
                {"error": f"Failed to send email: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]  # ← Add this
    
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(email=serializer.validated_data["email"])
        otp = serializer.validated_data["otp"]

        try:
            otp_obj = PasswordResetOTP.objects.filter(
                user=user, otp=otp, is_verified=False
            ).latest("created_at")
        except PasswordResetOTP.DoesNotExist:
            return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

        if otp_obj.is_expired():
            return Response({"error": "OTP expired"}, status=status.HTTP_400_BAD_REQUEST)

        otp_obj.is_verified = True
        otp_obj.save()

        return Response({"message": "OTP verified"}, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]  # ← Add this
    
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(email=serializer.validated_data["email"])

        if not PasswordResetOTP.objects.filter(user=user, is_verified=True).exists():
            return Response(
                {"error": "OTP not verified"}, status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(serializer.validated_data["password"])
        user.save()

        PasswordResetOTP.objects.filter(user=user).delete()

        return Response(
            {"message": "Password reset successful"}, status=status.HTTP_200_OK
        )

class UpdateRoleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        serializer = UserRoleUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Role updated successfully", "role": serializer.data['role']}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from hotels.models import HotelDataModel
from restaurants.models import RestaurantDataModel

class BusinessProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data
        
        # Determine model based on user role or category if sent (frontend sends category in step 1, but this API is called at end)
        # Frontend updates role first, so rely on user.role
        
        if user.role == 'Hotel':
            # Check if hotel already exists? Maybe allow multiple? For now assume one profile per user or create new.
            # BusinessLogin.jsx doesn't send badges/prices yet, so we use defaults/nulls.
            
            hotel = HotelDataModel.objects.create(
                owner=user,
                name=data.get('name'),
                city=data.get('city'),
                area=data.get('area'),
                description=data.get('description'),
                # Optional fields will be null/default
            )
            return Response({"message": "Hotel profile created", "id": hotel.id}, status=status.HTTP_201_CREATED)
            
        elif user.role == 'Restaurant': 
            restaurant = RestaurantDataModel.objects.create(
                owner=user,
                name=data.get('name'),
                city=data.get('city'),
                area=data.get('area'),
                description=data.get('description'),
            )
            return Response({"message": "Restaurant profile created", "id": restaurant.id}, status=status.HTTP_201_CREATED)
            
        else:
            return Response({"error": "Invalid role for business profile"}, status=status.HTTP_400_BAD_REQUEST)

class UserProfileUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def patch(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            user = serializer.save()
            
            # Construct explicit response to match LoginView format
            return Response({
                "message": "Profile updated successfully",
                "user": {
                    "id": user.id,
                    "first_name": user.first_name,
                    "email": user.email,
                    "phone": user.phone,
                    "role": getattr(user, "role", None),
                    "profile_image": user.profile_image.url if user.profile_image else None,
                }
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.delete()
        return Response({"message": "User account deleted successfully"}, status=status.HTTP_204_NO_CONTENT)