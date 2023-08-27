from django.db import models
from base.models import BaseModel
from django.contrib.auth.models import User, AbstractUser

# Create your models here.

class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name = 'profile')
    is_email_verified = models.BooleanField(default=False)
    email_token = models.CharField(max_length=100, null = True, blank=True)
    address_filled = models.BooleanField(default = False)
    profile_image = models.ImageField(upload_to = 'profile', null = True, blank=True)
    

class address(BaseModel):
    user_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name = 'user_profile', default=None)
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=10)
    landmark = models.CharField(max_length=100, null=True)
    mobile = models.CharField(max_length=15, null=True)
    alternate_mobile = models.CharField(max_length=15, null=True)