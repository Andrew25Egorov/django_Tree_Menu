"""my_tree_menu URL Configuration"""

from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('about/',
         TemplateView.as_view(template_name='about.html'),
         name='about'),
    path('contact/',
         TemplateView.as_view(template_name='contact.html'),
         name='contact'),
    path('products/',
         TemplateView.as_view(template_name='products.html'),
         name='products'),
    path('products/laptops/',
         TemplateView.as_view(template_name='laptops.html'),
         name='laptops'),
]
