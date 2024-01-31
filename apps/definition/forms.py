import os
import re
from django import forms
from django.utils.html import format_html
from apps.definition.models import UserProfile
from django.core.validators import MinValueValidator,MaxValueValidator

class UserProfileForm(forms.ModelForm):
    photo = forms.ImageField(required=False, label='Nova Foto de Perfil')
    description = forms.CharField(label='Descrição')

    class Meta:
        model = UserProfile
        fields = ['photo', 'phone_number', 'description']

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if description and len(description) > 100:
            raise forms.ValidationError('A descrição não pode ultrapassar 100 caracteres.')
        return description

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo:
            if photo.size > 5*1024*1024:  # limit photo size to 5MB
                raise forms.ValidationError('The photo is too large. It should be less than 5MB.')
        return photo

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        # Add your phone number validation logic here
        return phone_number

    def as_table(self):
        if self.instance.photo:
            return format_html(
                '<tr><th>{}</th><td><img src="{}" alt="Foto Atual" style="max-height: 100px;"></td></tr>',
                self['photo'].label,
                self.instance.photo.url
            )
        return super().as_table()

class AvaliacaoForm(forms.Form):
    estrelas = forms.IntegerField(
        label='Estrelas',
        widget=forms.NumberInput(attrs={'type': 'number', 'min': 0, 'max': 5}),
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    comentario = forms.CharField(
        label='Comentário',
        widget=forms.Textarea(attrs={'rows': 4})
    )
    
    
class SearchForm(forms.Form):
    search_query = forms.CharField(label='Pesquisar')
    
    