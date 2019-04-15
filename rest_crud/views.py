from django.shortcuts import render
from rest_framework import generics
from rest_framework.views import APIView, Response
from .models import Profile, Property, PropertyImage, Inquiry
from django.contrib.auth.models import User
from .serializers import (
    UserSerializer, ProfileSerializer, InquirySerializer,
    PropertySerializer, PropertyImageSerializer
)
from rest_framework.renderers import TemplateHTMLRenderer
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout
from django.contrib.auth.views import logout_then_login, LoginView
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from rest_framework.permissions import BasePermission
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class Creator(BasePermission):
    def has_permission(self, request, view):
        view_class = view.__class__.__name__
        is_seller = Profile.objects.get(pk=request.user.id).seller
        options = {1: is_seller, 0: not is_seller}
        return options[view_class == 'CreateEditPropertyView']


class ExtLogin(LoginView):
    def get_redirect_url(self):
        if self.request.path == '/login/':
            query = f'?user={self.request.user.id}'
            return f'/user/info/{query}'
        else:
            return '/'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add context data for search inputs in template
        # context['states'] = Property.objects.all().values('state').distinct()
        recent_props = Property.objects.all()[::-1][:3]
        images = list()
        for prop in recent_props:
            images.append(prop.propertyimage_set.all()[0].image.url)
        import pdb;pdb.set_trace()
        extra_context = {
            'get_login': self.request.user.is_anonymous,
            'usr_id': self.request.user.id,
            'user_serial': UserSerializer(), 
            'prof_serial': ProfileSerializer(),
            'top_featured': recent_props,
            'images': images
        }
        context.update(extra_context)
        return context


class CreateEditUserView(APIView):
    renderer_classes = (TemplateHTMLRenderer,)
    template_name = 'testuser.html'

    def get(self, request):
        return Response({
                    'user_serial': UserSerializer(),
                    'profile_serial': ProfileSerializer()
                }) 

    def post(self, request):
        clean_dat = {k: v for k, v in request.data.items() if v != ""}
        usr = request.user

        if not request.user.is_anonymous:
            user_serial = UserSerializer(usr, data=clean_dat, partial=True)
            prof = Profile.objects.get(pk=request.user.pk)
            prof_serial = ProfileSerializer(prof, data=clean_dat, partial=True)

            if user_serial.is_valid() and prof_serial.is_valid():
                user_serial.save()
                prof_serial.save()
                import pdb;pdb.set_trace()
                return redirect(request.META.get('HTTP_REFERER'))  

            return redirect('/user/')

        new_user_serial = UserSerializer(data=clean_dat)
        new_profile_serial = ProfileSerializer(data=clean_dat)
        import pdb;pdb.set_trace()
        if not (new_user_serial.is_valid() and new_profile_serial.is_valid()):
            return redirect('/user/')

        new_user_serial.save()
        new_user = User.objects.get(username=new_user_serial.data['username'])
        new_profile_serial.save(user=new_user)
        login(request, user=new_user)

        return redirect('/login/')


class ListUserView(APIView):
    renderer_classes = (TemplateHTMLRenderer,)
    template_name = 'index.html'

    def get(self, request):
        if len(request.query_params):
            usr = User.objects.get(pk=request.query_params.get('user'))
            usr.password = ''

            prof_json = ProfileSerializer(usr.profile).data
            prof_json['username'] = UserSerializer(usr).data['username']
            prof_json['account'] = 'Seller' if prof_json['seller'] else 'Buyer'

            props = Property.objects.filter(seller=usr)
            prop_data = [{'title': p.title, 'id': p.id} for p in props]
            
            return Response({
                'user_serial': UserSerializer(usr),
                'prof_serial': ProfileSerializer(usr.profile),
                'prof_data': prof_json,
                'prop_data': prop_data,
                'read_only_single_user': True,
                'is_self': request.user == usr
            })
        else:
            users = User.objects.all()
            users_data = [{'name': u.username, 'id': u.id} for u in users]
            return Response({
                'users': users_data
            })


class LogoutView(APIView):
    def get(self, request):
        return logout_then_login(request, login_url='/')


class CreateEditPropertyView(LoginRequiredMixin, APIView):
    login_url = '/login/'
    renderer_classes = (TemplateHTMLRenderer,)
    template_name = 'properties.html'
    permission_classes = (Creator,)
    style = {}

    def get(self, request):
        if len(request.query_params):
            prop = Property.objects.get(pk=request.query_params['id'])
            return Response({
                'property_serial': PropertySerializer(prop),
                'style': self.style,
                'is_update': True,
            })
        return Response({
                    'property_serial': PropertySerializer(),
                    'style': {},
                }) 

    def post(self, request):
        if len(request.query_params):
            clean_data = {k: v for k, v in request.data.items() if v != ""}
            pk = request.query_params['id']
            prop = Property.objects.get(pk=pk)
            serial = PropertySerializer(prop, data=clean_data, partial=True)
            if serial.is_valid():
                self.save_imgs(request.FILES, PropertyImageSerializer, prop.id)
                serial.save()
            return redirect(f'/property/list/?id={pk}')

        property_serial = PropertySerializer(data=request.data)
        if property_serial.is_valid():
            pk = property_serial.save(seller=request.user).pk
            self.save_imgs(request.FILES, PropertyImageSerializer, pk)  
            return redirect(f'/property/list/?id={pk}')

    def save_imgs(self, images, serial, prop_pk):
        img_list = dict(images).get('image', [])
        img_objs = [{'estate': prop_pk, 'image': img} for img in img_list]
        img_serials = [serial(data=img_data) for img_data in img_objs]

        for serial in img_serials:
            if serial.is_valid():
                serial.save()


class ListPropertyView(APIView):
    renderer_classes = (TemplateHTMLRenderer,)
    template_name = 'index.html'
    style = {}

    def get(self, request):
        import pdb;pdb.set_trace()
        params = {k: v for k, v in request.query_params.items()}
        props = Property.objects.all().filter(**params)    
        usr = request.user
        is_buyer, buyer_has_inqd = bool(), bool()
        inquiries = dict()
        is_owner = False

        if len(props) == 1 and props[0].seller == usr:
            is_owner = True
            inquiries = props[0].inquiry_set.all()
        elif len(props) == 1 and not usr.is_anonymous:
            is_buyer = not usr.profile.seller
            if is_buyer:
                query = {'buyer': usr.id, 'estate': props[0].id}
                buyer_has_inqd = len(Inquiry.objects.filter(**query))

        prop_objs = list()
        for prop in props:
            to_update = {
                'seller': prop.seller.username,
                'date': prop.listing_date,
                'images': prop.propertyimage_set.all()
                }
            prop_data = PropertySerializer(prop).data
            prop_data.update(to_update)
            prop_objs.append(prop_data)

        return Response({
            'prop_objs': prop_objs,
            'inquiries': inquiries,
            'user_serial': UserSerializer(),
            'prof_serial': ProfileSerializer(),
            'inq_serial': InquirySerializer(),
            'style': {},
            'read_only': True,
            'is_buyer': is_buyer,
            'buyer_and_inqd': buyer_has_inqd,
            'is_owner': is_owner,
            'is_property': True,
            'usr_id': usr.id,
            'is_anonymous': usr.is_anonymous
        })


class ListInquiryView(LoginRequiredMixin, APIView):
    login_url = '/login/'
    renderer_classes = (TemplateHTMLRenderer,)
    template_name = 'inquiries.html'
    style = {}

    def get(self, request):
        if not request.user.profile.seller:
            inqs = request.user.inquiry_set.all()
            return Response({
                'inquiries': inqs,
            })


class CreateEditInquiryView(LoginRequiredMixin, APIView):
    login_url = '/login/'
    renderer_classes = (TemplateHTMLRenderer,)
    template_name = 'inquiries.html'
    style = {}
    permission_classes = (Creator,)

    def get(self, request):
        if len(request.query_params):
            if request.query_params.get('inq_id', False):
                inq = Inquiry.objects.get(pk=request.query_params['inq_id'])
                return Response({
                    'Inq_Serial': InquirySerializer(inq),
                    'style': self.style
                })
            return Response({
                    'Inq_Serial': InquirySerializer(),
                    'style': self.style
                })

    def post(self, request):
        
        if request.data.get('new_inq', False):
            prop_id = request.META.get('HTTP_REFERER').split('=')[-1]
            inq_data = {
                'estate': prop_id,
                'buyer': request.user.id,
                'comment': request.data['comment']
            }
            inquiry = InquirySerializer(data=inq_data)
            if inquiry.is_valid():
                # buyer = request.user.profile
                # seller = prop.seller.profile
                # send_mail(
                #     f'New Inquiry',
                #     f'I have made an inquiry for {prop.title}.',
                #     'yamalik42@gmail.com',
                #     ['yash.malik@tothenew.com'],
                #     fail_silently=False,
                # )
                inquiry.save()
            return redirect('/property/list/')

        inq = Inquiry.objects.get(pk=request.query_params['inq_id'])
        data = {'comment': request.data['comment']}
        inq_serial = InquirySerializer(inq, data=data, partial=True)
        import pdb;pdb.set_trace()
        if inq_serial.is_valid():
            inq_serial.save()
        return redirect('/inquiry/api/list/') 


# class View(APIView):
#     renderer_classes = (TemplateHTMLRenderer,)
#     template_name = 'index.html'
#     style = {}

#     def get(self, request):
#         return Response({'get_home': True})
def PropertyPagination(request):
    props = Property.objects.all()
    num_pages = (len(props)//6) + 1
    paginator = Paginator(props, num_pages)
    page = request.GET.get('page', 1)
    
    try:
        props = paginator.page(page)
    except PageNotAnInteger:
        props = paginator.page(1)
    except EmptyPage:
        props = paginator.page(paginator.num_pages)
    
    return props
