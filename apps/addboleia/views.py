import json
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .models import Boleia, HistoricoBoleia
from .forms import BoleiaForm
import geocoder
from .models import PedidoBoleia
from django.conf import settings
from django.db.models import F
from django.http import JsonResponse
from datetime import timedelta
from django.utils import timezone
import logging
from djangoProject.huey_config import enviar_email_boleia_agendada
from googlemaps import Client
from django.template.loader import render_to_string
from django.utils.html import strip_tags
# para criar um tuplo na tabela userprofile
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from apps.definition.models import UserProfile, UserBlock

logger = logging.getLogger(__name__)


# Função para calcular ETA com base no atraso
def calcular_eta(data, hora):
    agora = timezone.now()
    boleia = timezone.make_aware(datetime.combine(data, hora))
    diff_minutos = (boleia - agora).total_seconds() / 60
    dias = int(diff_minutos // 1440)
    minutos = int(diff_minutos % 1440)

    eta = boleia + timedelta(days=dias, minutes=minutos)

    return eta


@login_required(login_url='/login/')
def agendar_boleia(request):
    form = BoleiaForm(request.POST or None)

    if request.method == 'POST':
        form = BoleiaForm(request.POST)
        if form.is_valid():
            # Se o formulário for válido, continue com o processamento
            boleia_instance = form.save(commit=False)
            boleia_instance.user = request.user

            origem_location = geocoder.osm(boleia_instance.origem)
            destino_location = geocoder.osm(boleia_instance.destino)

            if not origem_location or not destino_location:
                return JsonResponse({'success': False, 'errors': ['__all__: Endereço inválido']})

            boleia_instance.origem_latitude = origem_location.latlng[0] if origem_location else None
            boleia_instance.origem_longitude = origem_location.latlng[1] if origem_location else None
            boleia_instance.destino_latitude = destino_location.latlng[0] if destino_location else None
            boleia_instance.destino_longitude = destino_location.latlng[1] if destino_location else None

            if (
                    boleia_instance.origem_latitude is None
                    and boleia_instance.origem_longitude is None
                    and boleia_instance.destino_latitude is None
                    and boleia_instance.destino_longitude is None
            ):
                return JsonResponse(
                    {'success': False, 'errors': ['__all__: Não foi possível decodificar o endereço desejado']})

            min_latitude = 39.87625
            max_latitude = 41.20192
            min_longitude = -8.90665
            max_longitude = -7.85707

            if (
                    min_latitude <= boleia_instance.origem_latitude <= max_latitude
                    and min_longitude <= boleia_instance.origem_longitude <= max_longitude
                    and min_latitude <= boleia_instance.destino_latitude <= max_latitude
                    and min_longitude <= boleia_instance.destino_longitude <= max_longitude
            ):
                # Configure a chave da API do Google Maps
                api_key = 'AIzaSyA5T5hTNTE_29t3Hdilo470G35BpBzan4s'
                gmaps = Client(api_key)

                # Calcule o tempo estimado de viagem
                result = gmaps.distance_matrix(
                    (boleia_instance.origem_latitude, boleia_instance.origem_longitude),
                    (boleia_instance.destino_latitude, boleia_instance.destino_longitude),
                    mode="driving",
                )
                if 'rows' in result and result['rows']:
                    element = result['rows'][0]['elements'][0]
                    if 'duration' in element and 'value' in element['duration']:
                        duracao_viagem = element['duration']['value']  # em segundos

                        atraso_email = 1  # minutos de atraso para o email

                        boleia_instance.eta = calcular_eta(boleia_instance.data, boleia_instance.hora) + timedelta(
                            minutes=atraso_email + duracao_viagem // 60)
                        boleia_instance.save()

                        # Agende a tarefa do Huey para enviar o e-mail no momento correto
                        enviar_email_boleia_agendada.schedule(
                            eta=boleia_instance.eta,
                            args=[boleia_instance.user.email, boleia_instance.id]
                        )
                        return JsonResponse({'success': True, 'message': 'Boleia agendada com sucesso!'})

                return JsonResponse({'success': True, 'message': 'Boleia agendada com sucesso!'})
            else:
                return JsonResponse({'success': False, 'errors': ['__all__: Origem indisponível']})
        else:
            # Se houver erros no formulário, prepare as mensagens de erro
            form_errors = {}
            for field, errors in form.errors.items():
                form_errors[field] = errors

            # Retorne JSON com mensagens de erro
            return JsonResponse({'success': False, 'errors': form_errors})

    context = {'form': form}
    return render(request, 'agendar_boleia.html', context)


# ---------------------------------------------------------------------

from datetime import datetime


@login_required(login_url='/login/')
def home_page(request):
    """
    Exibe a página inicial com as boleias disponíveis e para quem não esteja bloqueado pelo utilizador especifico de acordo com o destino e data selecionados.

    Parameters:
    - request (HttpRequest): O objeto de solicitação HTTP.

    Returns:
    - render: Uma resposta renderizada com a página inicial e as boleias disponíveis.
    """
    user_profile, created = UserProfile.objects.get_or_create(user_id=request.user)

    destino_filtrado = request.GET.get('destino', None)
    data_filtrada = request.GET.get('data', None)
    data_hora_atuais = timezone.localtime(timezone.now())

    destinos_disponiveis = [choice[0] for choice in Boleia.DESTINOS_CHOICES]

    if destino_filtrado not in destinos_disponiveis:
        destino_filtrado = None

    # Obtém os ID dos utilizadores que estão bloqueados e que bloquearam o utilizador autenticado
    blocked_users_ids = list(UserBlock.objects.filter(blocker=request.user).values_list('blocked_id', flat=True))
    blocking_users_ids = list(UserBlock.objects.filter(blocked=request.user).values_list('blocker_id', flat=True))

    # Filtra as boleias excluindo as de usuários bloqueados ou que bloquearam o usuário
    boleias_existente = []
    for boleia in Boleia.objects.exclude(user_id__in=blocked_users_ids + blocking_users_ids):
        data_hora_boleia = timezone.make_aware(datetime.combine(boleia.data, boleia.hora))
        if data_hora_boleia >= data_hora_atuais:
            if destino_filtrado is None or boleia.destino == destino_filtrado:
                if data_filtrada is None or boleia.data == datetime.strptime(data_filtrada, '%Y-%m-%d').date():
                    boleias_existente.append(boleia)

    return render(request, 'home_page.html', {
        'boleias_existente': boleias_existente,
        'destinos': destinos_disponiveis,
        'destino_filtrado': destino_filtrado,
        'data_filtrada': data_filtrada
    })


@login_required(login_url='/login/')
def lista_boleias(request):
    """
    Exibe uma lista de boleias com base no destino e data selecionados.

    Parameters:
    - request (HttpRequest): O objeto de solicitação HTTP.

    Returns:
    - render: Uma resposta renderizada com a lista de boleias.
    """

    destino_filtrado = request.GET.get('destino', None)
    data_filtrada = request.GET.get('data', None)
    destinos_disponiveis = Boleia.DESTINOS_CHOICES

    if destino_filtrado not in dict(destinos_disponiveis).keys():
        destino_filtrado = None

    boleias = Boleia.objects.all()

    if destino_filtrado:
        boleias = boleias.filter(destino=destino_filtrado)

    if data_filtrada:
        try:
            data_formatada = datetime.strptime(data_filtrada, '%Y-%m-%d')
            boleias = boleias.filter(data=data_formatada)
        except ValueError:
            # Caso a data não seja válida, você pode tratar isso da maneira que achar adequada
            pass

    context = {
        'boleias': boleias,
        'destinos_disponiveis': destinos_disponiveis,
        'destino_filtrado': destino_filtrado,
        'data_filtrada': data_filtrada,
    }

    return render(request, 'addboleia/lista_boleias.html', context)


# lucas
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail


@login_required(login_url='/login/')
def detalhes_boleia(request, boleia_id):
    """
    Exibe os detalhes de uma boleia e processa a submissão do formulário de pedido.

    Parameters:
    - request (HttpRequest): O objeto de solicitação HTTP.
    - boleia_id (int): O ID da boleia.

    Returns:
    - render: Uma resposta renderizada com os detalhes da boleia.
    """

    boleia = get_object_or_404(Boleia, pk=boleia_id)
    success_message, error_message = None, None

    # Verificar se o usuário é o motorista da boleia
    if boleia.user == request.user:
        error_message = "Você não pode solicitar uma boleia para você mesmo."

    else:
        if request.method == 'POST':
            try:
                # Verificar se o usuário já fez um pedido para esta boleia
                pedido_existente = PedidoBoleia.objects.filter(boleia=boleia, passageiro=request.user).first()

                if pedido_existente:
                    # Verificar se o pedido anterior foi aceito, recusado ou ainda está pendente
                    if pedido_existente.aceito is True:
                        error_message = "Você já fez um pedido para esta boleia e ele foi aceito."
                    elif pedido_existente.aceito is False:
                        error_message = "Você já fez um pedido para esta boleia e ele foi recusado."
                    else:
                        error_message = "Você já fez um pedido para esta boleia anteriormente."

                else:
                    if boleia.vagas_ocupadas < boleia.vagas_disponiveis:
                        pedido = PedidoBoleia.objects.create(boleia=boleia, passageiro=request.user)
                        # Enviar e-mail ao motorista
                        subject = f'Interesse na sua boleia de {boleia.origem} para {boleia.destino}'
                        message = f'O passageiro {request.user.username} tem interesse na sua boleia. Clique no link para aceitar ou recusar:\n\n'
                        message += f'{request.build_absolute_uri("/addboleia/pedidos_do_motorista/")}'

                        from_email = settings.DEFAULT_FROM_EMAIL
                        to_email = boleia.user.email

                        send_mail(subject, message, from_email, [to_email], fail_silently=False)

                        success_message = 'Pedido de boleia enviado com sucesso. Aguarde a resposta do motorista.'
                    else:
                        error_message = "Desculpe, o número de passageiros já foi preenchido."

            except Exception as e:
                error_message = f"Ocorreu um erro ao enviar o pedido de boleia. Detalhes: {e}"

    return render(request, 'addboleia/detalhes_boleia.html',
                  {'boleia': boleia, 'success_message': success_message, 'error_message': error_message})


@login_required(login_url='/login/')
def pedidos_do_motorista(request):
    """
    Exibe os pedidos pendentes e processa as ações (aceitar ou recusar) dos pedidos.

    Parameters:
    - request (HttpRequest): O objeto de solicitação HTTP.

    Returns:
    - render: Uma resposta renderizada com a página de pedidos pendentes.
    """

    # Verificar se a solicitação é um POST (submissão do formulário)
    if request.method == 'POST':
        # Obter informações da solicitação do formulário
        action = request.POST.get('action')
        boleia_id = request.POST.get('boleia_id')
        passageiro_id = request.POST.get('passageiro_id')

        # Verificar a ação realizada no formulário
        if action == 'aceitar':
            # Lógica para aceitar o pedido
            pedido = PedidoBoleia.objects.filter(boleia__id=boleia_id, passageiro__id=passageiro_id).first()

            if pedido:
                # Atualizar o número de vagas ocupadas na boleia ao aceitar o pedido
                Boleia.objects.filter(id=boleia_id).update(vagas_ocupadas=F('vagas_ocupadas') + 1)

                # Marcar o pedido como aceito e salvar
                pedido.aceito = True
                pedido.save()

                # Enviar e-mail ao passageiro informando que a boleia foi aceita
                subject = 'Boleia Aceita'
                message = f'Sua solicitação para a boleia de {pedido.boleia.origem} para {pedido.boleia.destino} foi aceita.'
                from_email = 'uniway@outlook.pt'

                send_mail(subject, message, from_email, [pedido.passageiro.email], fail_silently=False)
        else:
            pedido = PedidoBoleia.objects.filter(boleia__id=boleia_id, passageiro__id=passageiro_id).first()

            if pedido:
                # Marcar o pedido como aceito e salvar
                pedido.aceito = False
                pedido.save()

                # Enviar e-mail ao passageiro informando que a boleia foi aceita
                subject = 'Boleia Recusada'
                message = f'Sua solicitação para a boleia de {pedido.boleia.origem} para {pedido.boleia.destino} foi recusada.'
                from_email = 'uniway@outlook.pt'

                send_mail(subject, message, from_email, [pedido.passageiro.email], fail_silently=False)

    # Pedidos Pendentes
    pedidos_pendentes = PedidoBoleia.objects.filter(aceito__isnull=True, boleia__user=request.user)
    print("Pending Requests Count:", pedidos_pendentes.count())

    # Pedidos Aceitos
    pedidos_aceitos = PedidoBoleia.objects.filter(aceito=True, boleia__user=request.user)

    # Pedidos Recusados
    pedidos_recusados = PedidoBoleia.objects.filter(aceito=False, boleia__user=request.user)

    # Renderizar a página de pedidos pendentes após a ação
    return render(
        request,
        'addboleia/pedidos_do_motorista.html',
        {
            'pedidos_pendentes': pedidos_pendentes,
            'pedidos_aceitos': pedidos_aceitos,
            'pedidos_recusados': pedidos_recusados,
        }
    )


@login_required(login_url='/login/')
def pedidos_do_passageiro(request):
    # Obter pedidos do passageiro logado
    pedidos_do_passageiro = PedidoBoleia.objects.filter(passageiro=request.user)

    return render(request, 'addboleia/pedidos_do_passageiro.html', {'pedidos_do_passageiro': pedidos_do_passageiro})


from django.http import JsonResponse


@login_required
def cancelar_boleia_ajax(request, boleia_id):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Usuário não autenticado.'})

    boleia = get_object_or_404(Boleia, id=boleia_id, user=request.user)

    passageiros_emails = list(
        PedidoBoleia.objects.filter(boleia=boleia)
        .exclude(aceito=False)
        .exclude(passageiro__email='')
        .values_list('passageiro__email', flat=True)
    )

    # Enviar e-mail aos passageiros
    subject = 'Boleia Cancelada'
    plain_message = (
        f"Exmo passageiro, a boleia com origem em {boleia.origem} e destino {boleia.destino}, "
        f"no dia {boleia.data.strftime('%d/%m/%Y')} às {boleia.hora.strftime('%H:%M')}, "
        f"foi cancelada pelo motorista. Pedimos desculpas pelo inconveniente."
    )
    send_mail(subject, plain_message, settings.DEFAULT_FROM_EMAIL, passageiros_emails)

    # Lista de e-mails dos passageiros (assumindo que há um campo que relaciona os pedidos à boleia)

    send_mail(subject, plain_message, settings.DEFAULT_FROM_EMAIL, passageiros_emails, html_message=plain_message)

    dados_pedidos = []
    for pedido in PedidoBoleia.objects.filter(boleia=boleia):
        dados_pedidos.append({
            'passageiro_username': pedido.passageiro.username,
            'origem': pedido.boleia.origem,
            'destino': pedido.boleia.destino,
            'data_pedido': pedido.data_pedido.strftime('%Y-%m-%d %H:%M:%S'),
            'motorista_username': boleia.user.username,
            'data_boleia': boleia.data.strftime('%Y-%m-%d'),
            'hora_boleia': boleia.hora.strftime('%H:%M:%S'),
            'aceito': pedido.aceito,
        })

    # Tenta abrir o arquivo JSON existente
    try:
        with open('apps/addboleia/pedidos_boleia.json', 'r') as arquivo_json:
            dados_json = json.load(arquivo_json)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        # Se o arquivo não existir ou não for um JSON válido, cria um dicionário vazio
        dados_json = {'pedidos': []}

    # Adiciona os novos dados aos existentes
    dados_json['pedidos'].extend(dados_pedidos)

    # Escrever os dados de volta no arquivo JSON
    from django.core.serializers.json import DjangoJSONEncoder

    with open('apps/addboleia/pedidos_boleia.json', 'w') as arquivo_json:
        json.dump(dados_json, arquivo_json, cls=DjangoJSONEncoder)

    # Mover a boleia para o histórico com o campo 'cancelada' marcado como True
    HistoricoBoleia.objects.create(

        user=boleia.user,
        destino=boleia.destino,
        origem=boleia.origem,
        data=boleia.data,
        hora=boleia.hora,
        vagas_disponiveis=boleia.vagas_disponiveis,
        vagas_ocupadas=boleia.vagas_ocupadas,
        cancelada=True
    )

    # para apagar a boleia da tabela addBoleia_boleia
    boleia.delete()

    return JsonResponse({'success': True, 'message': 'Boleia cancelada com sucesso.'})


from django.utils import timezone


def finalizar_boleia_ajax(request, boleia_id):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Usuário não autenticado.'})

    boleia = get_object_or_404(Boleia, id=boleia_id, user=request.user)

    # Mover a boleia para o histórico com o campo 'hora_chegada' preenchido
    HistoricoBoleia.objects.create(

        user=boleia.user,
        destino=boleia.destino,
        origem=boleia.origem,
        data=boleia.data,
        hora=boleia.hora,
        vagas_disponiveis=boleia.vagas_disponiveis,
        vagas_ocupadas=boleia.vagas_ocupadas,
        hora_chegada=timezone.now().strftime('%H:%M:%S')
    )

    # para apagar a boleia da tabela Boleia
    boleia.delete()

    return JsonResponse({'success': True, 'message': 'Boleia finalizada com sucesso.'})


def historico_motorista(request):
    # Obtenha todas as boleias do histórico para o motorista atual
    historico_boleias = HistoricoBoleia.objects.filter(user=request.user)

    context = {
        'historico_boleias': historico_boleias,
    }

    return render(request, 'addboleia/historico_motorista.html', context)


@login_required
def historico_passageiro(request):
    # Caminho para o arquivo JSON
    caminho_arquivo_json = 'apps/addboleia/pedidos_boleia.json'

    try:
        # Tentar abrir o arquivo JSON
        with open(caminho_arquivo_json, 'r') as arquivo_json:
            dados_json = json.load(arquivo_json)
    except FileNotFoundError:
        # Arquivo JSON não encontrado, retornar uma resposta vazia
        dados_json = {'pedidos': []}

    # Filtrar os dados do JSON para obter apenas os do usuário logado
    pedidos_usuario = [pedido for pedido in dados_json['pedidos'] if
                       pedido['passageiro_username'] == request.user.username]

    # Criar uma lista de dicionários para representar todos os pedidos
    historico_passageiro_todos = []

    for pedido in pedidos_usuario:
        dados_boleia = {
            'condutor': pedido['motorista_username'],
            'origem': pedido['origem'],
            'destino': pedido['destino'],
            'data': pedido['data_boleia'],
            'hora': pedido['hora_boleia'],
            'aceito': pedido.get('aceito', False),
        }
        historico_passageiro_todos.append(dados_boleia)

    # Separar os dados em aceitas e recusadas
    historico_passageiro_aceitas = [pedido for pedido in historico_passageiro_todos if pedido['aceito']]
    historico_passageiro_recusadas = [pedido for pedido in historico_passageiro_todos if
                                      pedido.get('aceito', False) is False]

    context = {
        'historico_passageiro_aceitas': historico_passageiro_aceitas,
        'historico_passageiro_recusadas': historico_passageiro_recusadas
    }

    return render(request, 'addboleia/historico_passageiro.html', context)


@login_required(login_url='/login/')
def tenho_interesse_boleia(request, boleia_id):
    """
    Registra o interesse de um passageiro que não estou bloqueado do utilizador em uma boleia e envia um email ao motorista.

    Parameters:
    - request (HttpRequest): O objeto de solicitação HTTP.
    - boleia_id (int): O ID da boleia.

    Returns:
    - JsonResponse: Uma resposta em formato JSON indicando o sucesso ou falha.
    """

    boleia = get_object_or_404(Boleia, pk=boleia_id)

    # Verificar se o usuário é o motorista da boleia
    if boleia.user == request.user:
        return JsonResponse({'success': False, 'message': 'Você não pode solicitar uma boleia para você mesmo.'})

    # Verifica se o user bloqueou o motorista da boleia ou foi bloqueado por ele
    if UserBlock.objects.filter(blocker=request.user, blocked=boleia.user).exists() or \
            UserBlock.objects.filter(blocker=boleia.user, blocked=request.user).exists():
        return JsonResponse(
            {'success': False, 'message': 'Nao pode solicitar interesse nesta boleia devido a restrições de bloqueio.'})

    try:
        # Verificar se o usuário já fez um pedido para esta boleia
        pedido_existente = PedidoBoleia.objects.filter(boleia=boleia, passageiro=request.user).first()

        if pedido_existente:
            # Verificar se o pedido anterior foi aceito, recusado ou ainda está pendente
            if pedido_existente.aceito is True:
                return JsonResponse(
                    {'success': False, 'message': 'Você já fez um pedido para esta boleia e ele foi aceito.'})
            elif pedido_existente.aceito is False:
                return JsonResponse(
                    {'success': False, 'message': 'Você já fez um pedido para esta boleia e ele foi recusado.'})
            else:
                return JsonResponse(
                    {'success': False, 'message': 'Você já fez um pedido para esta boleia anteriormente.'})
        else:
            # Verificar se o número de vagas disponíveis já foi preenchido
            if boleia.vagas_ocupadas >= boleia.vagas_disponiveis:
                return JsonResponse(
                    {'success': False, 'message': 'Desculpe, o número de passageiros já foi preenchido.'})

            pedido = PedidoBoleia.objects.create(boleia=boleia, passageiro=request.user)
            # Enviar e-mail ao motorista
            subject = f'Interesse na sua boleia de {boleia.origem} para {boleia.destino}'
            message = f'O passageiro {request.user.username} tem interesse na sua boleia. Clique no link para aceitar ou recusar:\n\n'
            message += f'{request.build_absolute_uri("/addboleia/pedidos_do_motorista/")}'

            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = boleia.user.email

            send_mail(subject, message, from_email, [to_email], fail_silently=False)

            return JsonResponse(
                {'success': True, 'message': 'Pedido de boleia enviado com sucesso. Aguarde a resposta do motorista.'})

    except Exception as e:
        return JsonResponse(
            {'success': False, 'message': f'Ocorreu um erro ao enviar o pedido de boleia. Detalhes: {e}'})
