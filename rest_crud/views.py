from django.shortcuts import render
from rest_framework import generics
from rest_framework.views import APIView, Response
from .models import Profile, Property, PropertyImage, Inquiry
from django.contrib.auth.models import User
from .serializers import (
    UserSerializer, ProfileSerializer, InquirySerializer
    PropertySerializer, PropertyImageSerializer
)
from rest_framework.renderers import TemplateHTMLRenderer
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout
from django.contrib.auth.views import logout_then_login, LoginView
from django.contrib.auth import login
from django.http import HttpResponseRedirect


class ExtendedLoginView(LoginView):
    def form_valid(self, form):
        """Security check complete. Log the user in."""
        login(self.request, form.get_user())
        query = f'?user={self.request.user.id}'
        url_with_query = f'{self.get_success_url()}{query}'
        return HttpResponseRedirect(url_with_query)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add context data for search inputs in template
        context['states'] = Property.objects.all().values('state').distinct()
        
        return context


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

        new_user_serial = UserSerializer(data=clean_dat)
        new_profile_serial = ProfileSerializer(data=clean_dat)

        if not (new_user_serial.is_valid() and new_profile_serial.is_valid()):
            return redirect('/user/')

        new_user_serial.save()
        new_user = User.objects.get(username=new_user_serial.data['username'])
        new_profile_serial.save(user=new_user)
        login(request, user=new_user)

        return redirect('/login/')


class ListUserView(APIView):
    renderer_classes = (TemplateHTMLRenderer,)
    template_name = 'testuser.html'

    def get(self, request):
        if len(request.query_params):
            usr = User.objects.get(pk=request.query_params.get('user'))

            profile = Profile.objects.get(pk=usr)
            prof_json = ProfileSerializer(profile).data
            prof_json['username'] = UserSerializer(usr).data['username']

            props = Property.objects.filter(seller=usr)
            prop_data = [{'title': p.title, 'id': p.id} for p in props]
                
            return Response({
                'prof_data': prof_json,
                'prop_data': prop_data
            })
        else:
            users = User.objects.all()
            users_data = [{'name': u.username, 'id': u.id} for u in users]
            return Response({
                'users': users_data
            })


class LogoutView(APIView):
    def get(self, request):
        return logout_then_login(request, login_url='/login/')


class CreatePropertyView(LoginRequiredMixin, APIView):
    login_url = '/login/'
    renderer_classes = (TemplateHTMLRenderer,)
    template_name = 'properties.html'

    def get(self, request):
        return Response({
                    'property_serial': PropertySerializer(),
                    'style': {},
                    'read_only': False
                }) 

    def post(self, request):
        property_serial = PropertySerializer(data=request.data)
        if property_serial.is_valid():
            prop_pk = property_serial.save(seller=request.user).pk
            pis = PropertyImageSerializer

            img_list = dict(request.FILES)['image']
            img_objs = [{'estate': prop_pk, 'image': img} for img in img_list]
            img_serials = [pis(data=img_data) for img_data in img_objs]
            for serial in img_serials:
                if serial.is_valid():
                    serial.save()
            import pdb;pdb.set_trace()


class ListPropertyView(APIView):
    renderer_classes = (TemplateHTMLRenderer,)
    template_name = 'properties.html'
    style = {}

    def get(self, request):
        props = Property.objects.all()
        params = {k: v for k, v in request.query_params.items()}
        props = props.filter(**params)      

        prop_objs = list()
        for prop in props:
            to_update = {
                'seller': prop.seller.username,
                'images': prop.propertyimage_set.all()
                }
            prop_data = PropertySerializer(prop).data
            prop_data.update(to_update)
            prop_objs.append(prop_data)
            import pdb;pdb.set_trace()
        return Response({
            'prop_objs': prop_objs,
            'style': {},
            'read_only': True
        })
        

class EditPropertyView(LoginRequiredMixin, APIView):
    login_url = '/login/'
    renderer_classes = (TemplateHTMLRenderer,)
    template_name = 'properties.html'
    style = {}

    def get(self, request, pk):
        import pdb;pdb.set_trace()


class ListCreateInquiryView(LoginRequiredMixin, APIView):
    login_url = '/login/'
    renderer_classes = (TemplateHTMLRenderer,)
    template_name = 'properties.html'
    style = {}

    def get(self, request):
        if len(request.query_params):
            return Response({
                'Inq_Serial'; InquirySerializer
            })