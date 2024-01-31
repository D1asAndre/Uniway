# No arquivo forms.py do seu aplicativo
from django import forms
import requests  # Certifique-se de ter a biblioteca requests instalada
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegistoForm(forms.Form):
    num_mec = forms.IntegerField()
    telemovel = forms.CharField(max_length=20, required=False)
    telefone = forms.CharField(max_length=20, required=False)
    email = forms.EmailField()
    nome = forms.CharField(max_length=25)
    apelido = forms.CharField(max_length=30)
    data_nascimento = forms.DateField()
    pais = forms.CharField(max_length=40, required=False)
    sexo = forms.CharField(max_length=1, required=False)
    password = forms.CharField(widget=forms.PasswordInput(render_value=False))


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

