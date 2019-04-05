from django.shortcuts import render
from rest_framework import generics
from rest_framework.views import APIView, Response
from .models import Profile, Property, PropertyImage, Inquiry
from django.contrib.auth.models import User
from .serializers import UserSerializer, ProfileSerializer
from .serializers import PropertySerializer, PropertyImageSerializer
from rest_framework.renderers import TemplateHTMLRenderer
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout
from django.contrib.auth.views import logout_then_login


class CreateEditUserView(APIView):
    renderer_classes = (TemplateHTMLRenderer,)
    template_name = 'testuser.html'

    def get(self, request):
        import pdb;pdb.set_trace()
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
        import pdb;pdb.set_trace()
        clean_dat = {k: v for k, v in request.data.items() if v != ""}
        usr = request.user

        if not request.user.is_anonymous:
            user_serial = UserSerializer(usr, data=clean_dat, partial=True)
            profile = Profile.objects.get(pk=request.user.pk)
            prof_serial = ProfileSerializer(usr, data=clean_dat, partial=True)

            if user_serial.is_valid() and prof_serial.is_valid():
                user_serial.save()
                prof_serial.save()

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


class RetrieveUserView(LoginRequiredMixin, APIView):
    login_url = '/login/'
    renderer_classes = (TemplateHTMLRenderer,)
    template_name = 'testuser.html'

    def get(self, request):
        if not request.user.is_anonymous:
            usr = request.user
            profile = Profile.objects.get(pk=usr)
            prof_json = ProfileSerializer(profile).data
            prof_json['username'] = UserSerializer(usr).data['username']
            
            return Response({
                'prof_data': prof_json
            })


class LogoutView(APIView):
    def get(self, request):
        return logout_then_login(request, login_url='/login/')


class CreateEditPropertyView(APIView):
    renderer_classes = (TemplateHTMLRenderer,)
    template_name = 'properties.html'

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
                    'property_serial': PropertySerializer(),
                    'image_serial': PropertyImageSerializer()
                }) 