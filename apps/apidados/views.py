import bcrypt
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from .forms import RegistoForm, LoginForm
import requests


def hash_password(password):
    # Gere um hash para a senha usando bcrypt
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode(
        'utf-8')  # Certifique-se de que está no formato de string para ser enviado na requisição


@user_passes_test(lambda user: user.is_superuser)
def criar_registro(request):
    if request.method == 'POST':
        form = RegistoForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            data['password'] = hash_password(data['password'])

            api_url = 'http://127.0.0.1:8025/registo/'

            response = requests.post(api_url, data=data)

            if response.status_code == 201:
                return redirect('listar_registo')
            else:
                error_message = response.text
                print(f"Erro ao criar registro: {error_message}")

    else:
        form = RegistoForm()

    return render(request, 'criar_registo.html', {'form': form})


@user_passes_test(lambda user: user.is_superuser)
def listar_registo(request):
    api_url = 'http://127.0.0.1:8025/registo/'
    response = requests.get(api_url)

    if response.status_code == 200:  # Código 200 geralmente significa solicitação bem-sucedida na API
        dados_api = response.json()  # Supondo que a API responda em formato JSON
        return render(request, 'listar_registo.html', {'dados_api': dados_api})
    else:
        # Lógica de manipulação de erro, se necessário
        return render(request, 'listar_registo.html', {'dados_api': None})


@user_passes_test(lambda user: user.is_superuser)
def excluir_registro(request, num_mec):
    api_url = f'http://127.0.0.1:8025/registo/{num_mec}/'
    if request.method == 'POST':
        response = requests.delete(api_url)

        if response.status_code == 204:
            return redirect('listar_registo')
        else:
            error_message = response.text
            print(f"Erro ao criar registro: {error_message}")
    else:
        # Se o método não for POST, renderize uma página de confirmação de exclusão
        return render(request, 'confirmar_exclusao.html', {'num_mec': num_mec})

    # Lógica de manipulação de erro se a solicitação não for bem-sucedida
    return render(request, 'listar_registo.html', {'dados_api': None})


@user_passes_test(lambda user: user.is_superuser)
def editar_registro(request, num_mec):
    api_url = f'http://127.0.0.1:8025/registo/{num_mec}/'

    if request.method == 'POST':
        form = RegistoForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            data['password'] = hash_password(data['password'])

            api_url = f'http://127.0.0.1:8025/registo/{num_mec}/'

            response = requests.put(api_url, data=data)

            if response.status_code == 200:
                return redirect('listar_registo')
            else:
                error_message = response.text
                print(f"Erro ao atualizar registro: {error_message}")

    else:
        # Se o método não for POST, obtenha os dados da API para preencher o formulário
        api_response = requests.get(api_url)

        if api_response.status_code == 200:
            registro_data = api_response.json()
            # Use o hash da senha obtido da API para preencher o formulário
            registro_data['password'] = '********'  # Ou outra marcação que você preferir
            form = RegistoForm(initial=registro_data)
        else:
            error_message = api_response.text
            print(f"Erro ao obter dados para atualização: {error_message}")
            form = RegistoForm()

    return render(request, 'editar_registo.html', {'form': form, 'num_mec': num_mec})

def login_view(request):
    if request.method == 'POST':
        # Se o formulário for enviado, valide os dados
        form = LoginForm(request.POST)

        if form.is_valid():
            provided_email = form.cleaned_data['email']
            provided_password = form.cleaned_data['password']

            # Faz uma solicitação GET à API
            api_url = "http://127.0.0.1:8025/registo/"
            response = requests.get(api_url)

            if response.status_code == 200:
                api_data = response.json()
            else:
                error_message = f"Falha ao obter dados da API. Código de status: {response.status_code}"
                return render(request, 'login_api.html', {'error_message': error_message, 'form': form})

            for user_data in api_data:
                email_from_api = user_data.get("email")
                encrypted_password_from_api = user_data.get("password")
                nome_from_api = user_data.get("nome")
                apelido_from_api = user_data.get("apelido")

                # Compara os dados fornecidos usando bcrypt
                if provided_email == email_from_api and bcrypt.checkpw(provided_password.encode('utf-8'),
                                                                       encrypted_password_from_api.encode('utf-8')):
                    # Derive o username do email (antes do '@')
                    username = provided_email.split('@')[0]

                    # Crie um usuário com base nos dados da API ou obtenha o usuário existente
                    user, created = User.objects.get_or_create(email=provided_email,
                                                               defaults={'password': encrypted_password_from_api,
                                                                         'username': provided_email.split('@')[0],
                                                                         'first_name': nome_from_api,
                                                                         'last_name': apelido_from_api})

                    if user is not None:
                        login(request, user)
                        return redirect('/addboleia/home/?destino=')
                    else:
                        # Trate o caso em que a autenticação falha
                        error_message = "Falha na autenticação do usuário."
                        return render(request, 'login_api.html', {'error_message': error_message, 'form': form})
    else:
        # Se for uma solicitação GET, cria um novo formulário
        form = LoginForm()

    return render(request, 'login_api.html', {'form': form})
