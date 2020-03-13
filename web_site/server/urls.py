"""server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import path, include
# from web_site.analysis.views import home_page
from django.http import HttpResponse
from django.shortcuts import render

# Default page
def empty_view(request):
    return render(request, 'index.html')

from django.views.generic import RedirectView
# from .tmp import home_page

urlpatterns = [
    path('admin/', admin.site.urls),
    path('pytar/', include(('analysis.urls','analysis'), namespace='analysis')),
    path('accounts/', include('django.contrib.auth.urls')),
    path("admin/", include('loginas.urls')),
    path('', empty_view)
]
