from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from apps.definition.models import UserProfile
from apps.definition.forms import UserProfileForm

@login_required()
def edit_profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user_id=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)

        if form.is_valid():
            form.save()
            return redirect('definition:view_profile')
        else:
            messages.error(request, 'Ocorreu um erro ao atualizar o perfil.')
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'definition/edit_profile.html', {'form': form})

@login_required()
def view_profile(request):
    # Get or create UserProfile instance for the current user
    user_profile, created = UserProfile.objects.get_or_create(user_id=request.user)

    # Redirect to the perfil_usuario view with the current user's username
    return redirect('definition:perfil_usuario', username=request.user.username)
    
#lucas
from django.shortcuts import render, get_object_or_404
from .models import UserProfile, AvaliacaoUsuario
from django.contrib.auth.models import User

# Importe a classe UserProfile no início do arquivo
from .models import UserProfile

'''
# views.py
def perfil_usuario(request, username):
    usuario = get_object_or_404(User, username=username)
    perfil = get_object_or_404(UserProfile, user_id=usuario)

    # Obtenha as avaliações do usuário
    avaliacoes = AvaliacaoUsuario.objects.filter(usuario_avaliado=usuario)

    # Use o método de instância corretamente
    default_photo_url = perfil.get_default_photo_url()

    context = {
        'perfil': perfil,
        'avaliacoes': avaliacoes,
        'default_photo_url': default_photo_url,
    }

    return render(request, 'definition/perfil_usuario.html', context)
'''
from django.shortcuts import render, get_object_or_404
from .models import UserProfile, AvaliacaoUsuario
from django.contrib.auth.models import User
from .forms import AvaliacaoForm

@login_required()
def perfil_usuario(request, username):
    usuario = get_object_or_404(User, username=username)
    perfil = get_object_or_404(UserProfile, user_id=usuario)
    avaliacoes = AvaliacaoUsuario.objects.filter(usuario_avaliado=usuario)

    # Formulário para avaliação
    form = AvaliacaoForm()

    boleias_ativas = perfil.boleias_ativas()

    context = {
        'perfil': perfil,
        'avaliacoes': avaliacoes,
        'boleias_ativas': boleias_ativas,
        'form': form,
    }

    return render(request, 'definition/perfil_usuario.html', context)

# views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import UserProfile, AvaliacaoUsuario
from django.contrib.auth.models import User
from .forms import AvaliacaoForm
@login_required()
def salvar_avaliacao(request, username):
    if request.method == 'POST':
        usuario_avaliado = get_object_or_404(User, username=username)
        avaliador = request.user  # ou a lógica que você usar para obter o avaliador

        form = AvaliacaoForm(request.POST)
        if form.is_valid():
            estrelas = form.cleaned_data['estrelas']
            comentario = form.cleaned_data['comentario']

            # Crie e salve a avaliação
            AvaliacaoUsuario.objects.create(
                avaliador=avaliador,
                usuario_avaliado=usuario_avaliado,
                estrelas=estrelas,
                comentario=comentario,
            )

            # Obtenha a instância do perfil do usuário
            perfil = get_object_or_404(UserProfile, user_id=usuario_avaliado)

            # Recalcule as avaliações no perfil do usuário, se a instância existir
            if perfil:
                perfil.recalcular_avaliacoes()

    return redirect('definition:perfil_usuario', username=username)

from .forms import SearchForm

@login_required()
def search_users(request):
    form = SearchForm(request.GET)
    results = []

    if form.is_valid():
        search_query = form.cleaned_data['search_query']
        # Realize a busca de usuários por nome ou username
        results = User.objects.filter(username__icontains=search_query)

    return render(request, 'definition/search_results.html', {'form': form, 'results': results})