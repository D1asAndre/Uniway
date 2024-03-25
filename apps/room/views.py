import logging
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, reverse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden

from .models import Room, Message
from apps.addboleia.models import Boleia
import uuid
from django.http import Http404
from django.db.models import Q
from django.contrib.auth.models import User

from ..definition.models import UserBlock

logger = logging.getLogger(__name__)


@login_required
def accessible_rooms(request):
    try:
        # Obtém todas as salas onde o utilizador da sessão é user1 ou user2
        user_rooms = Room.objects.filter(Q(user1=request.user) | Q(user2=request.user))
        return render(request, 'room/accessible_rooms.html', {'user_rooms': user_rooms})

    except Room.DoesNotExist:
        raise Http404("No accessible rooms for the user")


@login_required
def room(request, slug):
    try:
        room = Room.objects.get(slug=slug)
        logger.info(f" room with slug {slug} from the database.")

        # Verifica se o utilizador autenticado é o user1 ou o user2 da sala
        if request.user == room.user1 or request.user == room.user2:
            messages = Message.objects.filter(room=room)[0:25]
            logger.info(f" {len(messages)} messages for room {slug} from the database.")

            return render(request, 'room/room.html', {'room': room, 'messages': messages})
        else:
            return HttpResponseForbidden("Não tens permissões para esta sala! Baza seu hàckaro")

    except Room.DoesNotExist:
        raise Http404("Room does not exist")


@login_required
def create_chat_room(request):
    logger.info("Entering create_chat_room view")
    name_slug_uuid = None

    if request.method == 'POST':
        boleia_id = request.POST.get('boleia_id')
        session_id = request.POST.get('session_id')

        user1 = get_object_or_404(User, pk=session_id)
        user2 = get_object_or_404(User, pk=boleia_id)

        #Verificar se algum user está bloqueado
        if UserBlock.objects.filter(blocker=user1, blocked=user2).exists() or UserBlock.objects.filter(blocker=user2, blocked=user1).exists():
            logger.info("One of the users is blocked. Chat room creatin aborted.")
            return JsonResponse({'status': 'error', 'message': 'Está bloqueado pelo utilizador'})

        try:
            logger.info(f"Attempting to create chat room for boleia_id={boleia_id}, session_id={session_id}")

            # Verifica se a sala de chat já existe
            rooms = Room.objects.filter(
                Q(user1=session_id, user2=boleia_id) | Q(user1=boleia_id, user2=session_id)
            ).first()

            if not rooms:
                # Cria uma nova sala de chat se não existir
                name_slug_uuid = uuid.uuid4()
                rooms = Room(user1_id=session_id, user2_id=boleia_id, name=name_slug_uuid, slug=name_slug_uuid)
                rooms.save()
                logger.info(f"Chat room {name_slug_uuid} created and saved to the database.")
            else:
                name_slug_uuid = rooms.slug

            # Redireciona para a página correspondente à sala de chat
            logger.info(f"Redirecting to: {name_slug_uuid}")
            return JsonResponse(
                {'status': 'success', 'room_url': reverse('room:room', kwargs={'slug': name_slug_uuid})})

        except Exception as e:
            logger.error(f"Error creating or retrieving chat room: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)})

    logger.warning("Invalid request method")
    return JsonResponse({'status': 'error'})
