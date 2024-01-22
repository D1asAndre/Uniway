from django.urls import path
from .views import *

urlpatterns = [
    path('criar/registo/', criar_registro, name='criar_registo'),
    path('listar/registo/', listar_registo, name='listar_registo'),
    path('excluir/registo/<int:num_mec>/', excluir_registro, name='excluir_registro'),
    path('editar/registo/<int:num_mec>/', editar_registro, name='editar_registro'),
    path('login/', login_view, name='login_api'),
]
