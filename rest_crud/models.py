from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinValueValidator

re_phone_pattern = "^[0-9]{10}$"
re_name_pattern = "^[A-Za-z]+$"
re_zip_pattern = "^[0-9]{6}$"


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True
    )
    first_name = models.CharField(
        max_length=21,
        validators=[RegexValidator(re_name_pattern)]
    )
    last_name = models.CharField(
        max_length=21,
        validators=[RegexValidator(re_name_pattern)]
    )
    phone = models.CharField(
        max_length=10,
        validators=[RegexValidator(re_phone_pattern)]
    )
    seller = models.BooleanField(null=False, blank=False)
    email = models.EmailField(null=False, blank=False, unique=True)
    description = models.TextField(max_length=442)
    image = models.ImageField(upload_to='users/')


class Property(models.Model):
    title = models.CharField(max_length=21, null=False, blank=False)
    address = models.CharField(max_length=21, null=False, blank=False)
    city = models.CharField(max_length=21, null=False, blank=False)
    state = models.CharField(max_length=21, null=False, blank=False)
    zip_code = models.CharField(
        max_length=21,
        validators=[RegexValidator(re_zip_pattern)]
    )
    price = models.IntegerField(validators=[MinValueValidator(1)])
    bedroom = models.IntegerField(validators=[MinValueValidator(1)])
    bathroom = models.IntegerField(validators=[MinValueValidator(1)])
    square_feet = models.IntegerField(validators=[MinValueValidator(1)])
    lot_size = models.IntegerField(validators=[MinValueValidator(1)])
    garage = models.IntegerField(validators=[MinValueValidator(0)])
    listing_date = models.DateField(auto_now_add=True)
    description = models.TextField(max_length=442)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)


class PropertyImage(models.Model):
    image = models.ImageField(upload_to='properties/')
    estate = models.ForeignKey(Property, on_delete=models.CASCADE)


class Inquiry(models.Model):
    comment = models.TextField(max_length=442)
    estate = models.ForeignKey(Property, on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    sent_date = models.DateField(auto_now_add=True)
