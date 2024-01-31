import datetime
from django import forms
from .models import Boleia
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class BoleiaForm(forms.ModelForm):

    class Meta:
        model = Boleia
        fields = ['origem', 'destino', 'vagas_disponiveis', 'data', 'hora']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'hora': forms.TimeInput(attrs={'type': 'time'}),

        }

    def clean(self):
        cleaned_data = super().clean()
        data = cleaned_data.get('data')
        hora = cleaned_data.get('hora')
        vagasD = cleaned_data.get('vagas_disponiveis', 0)

        if vagasD < 1 or vagasD > 8:
            raise forms.ValidationError('Número de vagas inválido')
            # combina a data e a hora para verificar se é valido
        if data and hora:
            try:
                datetime_boleia = timezone.make_aware(
                    timezone.datetime.combine(data, hora)
                )
            except ValueError:
                raise forms.ValidationError('A data ou hora fornecida é inválida.')

            if datetime_boleia < timezone.now():
                raise forms.ValidationError('A data ou hora fornecida é inválida.')

        return cleaned_data