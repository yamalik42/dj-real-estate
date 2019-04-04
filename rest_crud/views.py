from django.shortcuts import render
from rest_framework import generics
from rest_framework.views import APIView, Response
from .models import Profile, Property, PropertyImage, Inquiry
from django.contrib.auth.models import User
from .serializers import UserSerializer, ProfileSerializer
from PIL import Image
from rest_framework.renderers import TemplateHTMLRenderer
from django.shortcuts import get_object_or_404, redirect
from .forms import ProfileForm, UserForm
from django.contrib.auth import hashers as Hash
from django.contrib.auth import password_validation as validator


class CreateEditUserView(APIView):
    renderer_classes = (TemplateHTMLRenderer,)
    template_name = 'testuser.html'

    def get(self, request):
        # import pdb;pdb.set_trace()
        if not request.user.is_anonymous:
            profile = Profile.objects.get(pk=request.user)
            request.user.password = ""
            return Response({
                    'user_serial': UserSerializer(request.user),
                    'profile_serial': ProfileSerializer(profile)
                })

        return Response({
                    'user_serial': UserSerializer(),
                    'profile_serial': ProfileSerializer()
                }) 

    def post(self, request):
        nonblank_data = {k: v for k, v in request.data.items() if v != ""}

        if not request.user.is_anonymous:
            user_serial = UserSerializer(
                                request.user,
                                data=nonblank_data,
                                partial=True
                            )

            profile = Profile.objects.get(pk=request.user.pk)
            profile_serial = ProfileSerializer(
                                    profile,
                                    data=nonblank_data,
                                    partial=True
                                )
            
            if user_serial.is_valid() and profile_serial.is_valid():
                user_serial.save()
                profile_serial.save()
                return redirect('/admin/')
                
            return redirect('/user/')

        new_user = UserSerializer(data=nonblank_data)
        new_profile = ProfileSerializer(data=nonblank_data)

        if not (new_user.is_valid() and new_profile.is_valid()):
            return redirect('/user/')
        
        new_user.save()
        saved_user = User.objects.get(username=new_user.data['username'])
        new_profile.save(user=saved_user)

        return redirect('/admin/')


class CheckLoginView(APIView):
    renderer_classes = (TemplateHTMLRenderer,)
    template_name = 'login.html'

    def get(self, request):
        return Response({'serializer': UserSerializer})
    
    def post(self, request):
        import pdb;pdb.set_trace()
