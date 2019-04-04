from rest_framework import serializers
from .models import Profile, Property, PropertyImage, Inquiry
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password


class ProfileSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True, required=False)
    seller = serializers.BooleanField(required=False)
    phone = serializers.CharField(required=False)

    class Meta:
        model = Profile
        exclude = ('user',)

    def create(self, validated_data):
            if 'seller' not in validated_data:
                validated_data['seller'] = False
            return super(ProfileSerializer, self).create(validated_data)


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(help_text="")

    class Meta:
        model = User
        fields = ('username', 'password')

    def create(self, validated_data):
        p_word = validated_data.get('password')
        validated_data['password'] = make_password(p_word)
        return super(UserSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        if 'password' in validated_data:
            instance.password = make_password(validated_data.get('password'))
        instance.save()
        return instance


class PropertySerializer(serializers.ModelSerializer):
    seller = serializers.PrimaryKeyRelatedField(
        many=False,
        queryset=User.objects.all()
    )

    class Meta:
        model = Property
        exclude = ('listing_date',)


class PropertyImageSerializer(serializers.ModelSerializer):
    estate = serializers.PrimaryKeyRelatedField(
        many=False,
        queryset=Property.objects.all()
    )

    class Meta:
        model = PropertyImage
        fields = '__all__'


class InquirySerializer(serializers.ModelSerializer):
    estate = serializers.PrimaryKeyRelatedField(
        many=False,
        queryset=Property.objects.all()
    )

    class Meta:
        model = Inquiry
        exclude = ('sent_date',)