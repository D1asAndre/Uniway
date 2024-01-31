from django.urls import path,include

from . import views

app_name = 'room'


urlpatterns = [
    path('accessible_rooms/', views.accessible_rooms, name='accessible_rooms'),
    path('<slug:slug>/', views.room, name='room'),
    path('rooms/create_chat_room/', views.create_chat_room, name='create_chat_room'), #ajax para enviar os dados
    

]