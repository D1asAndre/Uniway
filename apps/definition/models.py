from datetime import timezone
import os
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from traitlets import default



# Create your models here.
class UserProfile(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='media/profile_photos/', blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    description = models.TextField(blank=True, null=True, default="Eu uso a Uniway!")
    media_avaliacoes = models.FloatField(default=0)
    total_avaliacoes = models.PositiveIntegerField(default=0)
   
    def recalcular_avaliacoes(self):
        # Obtenha todas as avaliações para o usuário
        avaliacoes = AvaliacaoUsuario.objects.filter(usuario_avaliado=self.user_id)

        # Calcule a média das avaliações e atualize os campos no perfil do usuário
        total_estrelas = sum(avaliacao.estrelas for avaliacao in avaliacoes)
        self.total_avaliacoes = len(avaliacoes)

        if self.total_avaliacoes > 0:
            self.media_avaliacoes = total_estrelas / self.total_avaliacoes
        else:
            self.media_avaliacoes = 0

        # Salve as alterações no banco de dados
        self.save()

    from django.utils import timezone

    def __str__(self):
        return self.user_id.username

    def get_default_photo_url(self):
        return '/media/media/profile_photos/photo_perfil.jpg'

    def boleias_ativas(self):
        from apps.addboleia.models import Boleia
        return Boleia.objects.filter(user=self.user_id)
    
    def get_full_name(self):
        return f"{self.user_id.first_name} {self.user_id.last_name}"


class AvaliacaoUsuario(models.Model):
    avaliador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='avaliador')
    usuario_avaliado = models.ForeignKey(User, on_delete=models.CASCADE, related_name='usuario_avaliado')
    estrelas = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    comentario = models.TextField(blank=True, null=True)
    data_avaliacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Avaliação de {self.avaliador.username} para {self.usuario_avaliado.username}"