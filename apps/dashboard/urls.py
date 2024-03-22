from django.urls import path, include
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboardView, name='indexDash'),
    path('listar/', views.listarRegistos, name='listar'),
    path('listar/<int:id>/', views.listarRegistosPorId, name='listarId'),
]
