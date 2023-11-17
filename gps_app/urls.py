from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('mapa', views.mapa, name='mapa'),
    path('api/coordinates', views.gps_coordinates, name='gps_coordinates'),
    path('gps-data/', views.gps_data_list, name='gps_data_list'),
    path('update_name/', views.update_device_name, name='update_device_name'),
    path('update_cercado_to_device/', views.update_cercado_to_device, name='update_cercado_to_device'),
    path('config_cercado/', views.config_cercado, name='config_cercado'),
    path('remove_cercado/', views.remove_cercado, name='remove_cercado'),
    path('example/', views.example, name='example')
]