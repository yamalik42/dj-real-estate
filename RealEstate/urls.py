"""RealEstate URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from rest_crud import views
from . import settings
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', views.CreateEditUserView.as_view(), name='next'),
    path('user/info/', views.ListUserView.as_view(), name='profile'),
    path('user/api', views.CreateEditUserView.as_view()),
    path(
        'login/',
        views.ExtendedLoginView.as_view(redirect_authenticated_user=True),
        name='login'
    ),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('property/create/', views.CreatePropertyView.as_view()),
    path('property/list/', views.ListPropertyView.as_view()),
    path('property/edit/<int:order_by>/', views.EditPropertyView.as_view()),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)