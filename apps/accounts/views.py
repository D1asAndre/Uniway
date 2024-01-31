import os
import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from .forms import UserForm
import random
import string
from django.core.mail import send_mail
from django.contrib.auth.hashers import check_password
from django.contrib.auth import get_user_model
from .forms import ActivationForm
from django.contrib.auth.models import User
from .forms import ActivationForm
import json
from django.contrib.auth.hashers import make_password
from django.http import HttpResponseBadRequest

API_KEY = '54191be863167faa94a0d39937e12bceb5cc63d3'


def verify_email(email, api_key):
    """
    Função para verificar a validade de um endereço de e-mail usando um serviço de verificação.

    Args:
        email (str): O endereço de e-mail a ser verificado.
        api_key (str): A chave de API fornecida pelo serviço de verificação.

    Returns:
        bool: True se o e-mail for válido, False caso contrário.

    Raises:
        requests.exceptions.RequestException: Se ocorrer um erro na solicitação HTTP.
    """

    if not email.endswith("@ua.pt"):
        return False

    url = f"https://api.hunter.io/v2/email-verifier?email={email}&api_key={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        status = data['data']['status']
        if status == 'valid':
            return True
        else:
            return False
    else:
        return False


# Caminho para o arquivo JSON que armazenará os códigos
CODES_JSON_PATH = os.path.join(os.path.dirname(__file__), 'codes.json')


# Função para gerar um código de ativação aleatório de 6 dígitos
def generate_activation_code():
    return ''.join(random.choice(string.digits) for _ in range(6))


# Função para salvar o email e código de ativação em um arquivo JSON
def save_activation_code(email, code):
    activation_data = {}
    try:
        with open('activation_data.json', 'r') as file:
            activation_data = json.load(file)
    except FileNotFoundError:
        pass

    activation_data[email] = code

    with open('activation_data.json', 'w') as file:
        json.dump(activation_data, file)


# Função para ler os códigos do arquivo JSON
def load_codes_from_json():
    if os.path.exists(CODES_JSON_PATH):
        with open(CODES_JSON_PATH, 'r') as json_file:
            return json.load(json_file)
    return {}


def send_activation_email(email, activation_code):
    subject = 'Código de Ativação'
    message = f'Seu código de ativação é: {activation_code}'
    from_email = 'uniway@outlook.pt'
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)


def home(request):
    template_name = 'accounts/home.html'
    context = {}

    if request.method == 'POST':
        user_form = UserForm(request.POST)
        if user_form.is_valid():
            email = user_form.cleaned_data['email']
            username = user_form.cleaned_data['username']

            if not verify_email(email, API_KEY):
                return HttpResponseBadRequest("O email não é válido ou não pertence à universidade.")

            if get_user_model().objects.filter(email=email).exists() or get_user_model().objects.filter(
                    username=username).exists():
                messages.error(request, 'Já existe um usuário com esse email.')
                return redirect('user_register')

            c = user_form.save(commit=False)
            c.is_valid = False
            c.is_active = False

            #c.password = make_password(c.password)
            c.save()

            # user = user_form.save()  # Salva o novo usuário no banco de dados
            activation_code = generate_activation_code()
            save_activation_code(c.email, activation_code)
            send_activation_email(c.email, activation_code)

            messages.success(request, 'Verifique seu email para obter o código de ativação.')
            return redirect('activate_account')
        else:
            messages.error(request, 'Erro no formulário. Por favor, preencha corretamente.')
    else:
        user_form = UserForm()

    context['user_form'] = user_form
    return render(request, template_name, context)


def user_login(request):
    template_name = 'accounts/user_login.html'
    if request.method == 'POST':
       # username = request.POST['username']
        username_or_email = request.POST.get('username')
        password = request.POST['password']
        '''
        try:
            user = get_user_model().objects.get(username_or_email)

          #  user = get_user_model().objects.get(username=username)
        except:
            messages.error(request, 'Credenciais inválidas')
            return render(request, template_name, {})
         '''
        
        if '@' in username_or_email:
            # Se o caractere "@" estiver presente, assume que é um e-mail
            try:
                user = get_user_model().objects.get(email=username_or_email)
            except:
                messages.error(request, 'Credenciais inválidas')
                return render(request, template_name, {})
        else:
            # Senão, assume que é um nome de usuário
            try:
                user = get_user_model().objects.get(username=username_or_email)
            except:
                messages.error(request, 'Usuário ou senha incorreta!')
                return render(request, template_name, {})


        # Verifica se a senha fornecida coincide com a senha encriptada no banco de dados
        if user and check_password(password, user.password):
            if user.is_active:
                login(request, user)
                return redirect('/addboleia/home/?destino=')
            else:
                messages.warning(request, 'A conta ainda não foi verificada!')
                return redirect('/')
        else:
            messages.error(request, 'Usuário ou senha incorreta!')
            

    return render(request, template_name, {})


# View para ativação de conta
def activate_account(request):
    """
    View para ativar a conta do usuário com um código de ativação.

    Permite que o usuário insira o código de ativação recebido por email para ativar a sua conta.

    Args:
        request (HttpRequest): O objeto de solicitação HTTP.

    Returns:
        HttpResponse: Redireciona para a página do perfil do usuário se o código for válido, senão exibe uma mensagem de erro.
    """

    if request.method == 'POST':
        activation_form = ActivationForm(request.POST)

        if activation_form.is_valid():
            email = activation_form.cleaned_data['email']
            activation_code = activation_form.cleaned_data['activation_code']

            try:
                with open('activation_data.json', 'r') as file:
                    activation_data = json.load(file)

                if email in activation_data and activation_data[email] == activation_code:
                    user = User.objects.get(email=email)

                    if not user.is_active:
                        user.is_active = True
                        user.save()
                        login(request, user)
                        messages.success(request, 'Sua conta foi ativada com sucesso.')
                    else:
                        messages.info(request, 'Sua conta já está ativada.')

                    return redirect('user_profile')
                else:
                    messages.warning(request,
                                     'Código de ativação inválido. Por favor, verifique o código e tente novamente.')
            except FileNotFoundError:
                messages.error(request, 'Código de ativação não encontrado. Por favor, registre-se novamente.')
                return redirect('home')
        else:
            messages.error(request, 'Erro no formulário. Por favor, preencha corretamente.')

    activation_form = ActivationForm()
    context = {'activation_form': activation_form}
    return render(request, 'accounts/activate_account.html', context)


@login_required(login_url='/login/')
def user_profile(request):
    template_name = 'home_page.html'
    return render(request, template_name, {})


@login_required(login_url='/login/')
def user_logout(request):
    logout(request)
    messages.success(request, 'Você saiu do sistema.')
    return redirect('user_login')
