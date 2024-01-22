from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth.forms import UserCreationForm



'''
class UserForm(forms.ModelForm):
    password = forms.CharField(label='Senha', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password']
        labels = {
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'username': 'Nome de Usuário',
            'email': 'E-mail',
        }
'''  

class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']
        labels = {
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'username': 'Nome de Usuário',
            'email': 'E-mail',
        }

'''
         def clean_password(self):
        # Obtenha a senha do formulário
        password = self.cleaned_data.get('password')

        # Encripte a senha usando make_password e imprima para verificação
        hashed_password = make_password(password)
        print(f'Senha Original: {password}')
        print(f'Senha Encriptada: {hashed_password}')

        # Retorne a senha encriptada
        return hashed_password
'''

class ActivationForm(forms.Form):
    email = forms.EmailField(label='E-mail', max_length=254)
    activation_code = forms.CharField(max_length=6, label='Código de Ativação', widget=forms.PasswordInput)

     