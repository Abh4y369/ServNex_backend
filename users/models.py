from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from random import randint
from django.db import models
from django.conf import settings
from django.utils import timezone
import datetime

User = settings.AUTH_USER_MODEL

# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self,email,password=None,**extra_fields):
        if not email:
            raise ValueError("Email is a required field")
        
        email= self.normalize_email(email)
        user= self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self,email,password=None,**extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email,password,**extra_fields)

class User(AbstractUser):
    role_options=[
        ("Hotel",'Hotel'),
        ("Restaurant","Restaurant"),
        ("Saloon","Saloon"),
        ("User","User"),
        ("Business","Business"),
    ]
    email=models.EmailField(max_length=200, unique=True)
    phone=models.CharField(max_length=15,unique=True,null=True, blank=True)
    username=models.CharField(max_length=200, null=True, blank=True)
    role=models.CharField(max_length=20,choices=role_options,default="User")
    profile_image=models.ImageField(upload_to='profiles/', null=True, blank=True)
    # is_verified=models.BooleanField(default=True)
    # otp=models.CharField(max_length=10,null=True,blank=True)
    # def generate_otp(self):
    #     otp_number=str(randint(1000,9000))+str(self.id)
    #     self.otp=otp_number
    #     self.save()

    objects=CustomUserManager()

    USERNAME_FIELD= "email"

    REQUIRED_FIELDS=[

    ]
    def __str__(self):
        return self.first_name
    
class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + datetime.timedelta(minutes=10)

    def __str__(self):
        return f"{self.user} - {self.otp}"