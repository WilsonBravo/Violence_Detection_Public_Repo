from django.urls import path
from django.urls import path, re_path, reverse
from django.shortcuts import redirect

from . import views

urlpatterns = [
    path('home', views.index, name='home'),
    path('start_system/', views.start_system, name='start_system'),
    path('stop_system/', views.stop_system, name='stop_system'),
    # Redirecciona /admin/home/configuraciones_generales/ a /admin/home/configuraciones_generales/1/change/
    path('admin/home/configuraciones_generales/', lambda request: redirect('/admin/home/configuraciones_generales/1/change/')),
    path('admin/home/configuraciones_del_sistema/', lambda request: redirect('/admin/home/configuraciones_del_sistema/1/change/')),
   
]
