from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from apps.definition.views import edit_profile, view_profile, perfil_usuario, salvar_avaliacao, search_users, \
    block_users, unblock_users

app_name = 'definition'

urlpatterns = [
    path('edit-profile/', edit_profile, name='edit_profile'),
    path('view-profile/', view_profile, name='view_profile'),
    path('perfil/<str:username>/', perfil_usuario, name='perfil_usuario'),
    path('salvar_avaliacao/<str:username>/', salvar_avaliacao, name='salvar_avaliacao'),
    path('search/', search_users, name='search_users'),
    path('block/<int:user_id>/', block_users, name='block_users'),
    path('unblock/<int:user_id>/', unblock_users, name='unblock_users')



] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
