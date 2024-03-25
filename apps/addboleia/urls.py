from django import views
from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required



app_name = 'addboleia'

urlpatterns = [
    path('agendar_boleia/', views.agendar_boleia, name='agendar_boleia'),
    path('home/', views.home_page, name='home_page'),
    path('lista_boleias/', views.lista_boleias, name='lista_boleias'),
    path('boleia/<int:boleia_id>/', views.detalhes_boleia, name='detalhes_boleia'), #lucas
    path('pedidos_do_motorista/', views.pedidos_do_motorista, name='pedidos_do_motorista'),
    path('pedidos_do_passageiro/', views.pedidos_do_passageiro, name='pedidos_do_passageiro'),
    path('cancelar_boleia_ajax/<int:boleia_id>/', views.cancelar_boleia_ajax, name='cancelar_boleia_ajax'),
    path('cancelar_boleia_passageiro/<int:boleia_id>/', views.cancelar_pedido_passageiro, name='cancelar_boleia_passageiro'),
    path('finalizar_boleia_ajax/<int:boleia_id>/', views.finalizar_boleia_ajax, name='finalizar_boleia_ajax'),
    path('historico_motorista/', views.historico_motorista, name='historico_motorista'),
    path('historico_passageiro/', views.historico_passageiro, name='historico_passageiro'),
    path('tenho_interesse_boleia/<int:boleia_id>/', views.tenho_interesse_boleia, name='tenho_interesse_boleia'),

    

]
