from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime

class Boleia(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    origem = models.CharField(max_length=255)
    DESTINOS_CHOICES = [
        ('Escola Superior Aveiro Norte',
         'Escola Superior de Design, Gestão e Tecnologias da Produção Aveiro Norte (ESAN)'),
        ('Escola Superior de Tecnologia e Gestão de Águeda',
         'Escola Superior de Tecnologia e Gestão de Águeda (ESTGA)'),
        ('Escola Superior de Saúde da Universidade de Aveiro',
         'Escola Superior de Saúde da Universidade de Aveiro (ESSUA)'),
        ('Instituto Superior de Contabilidade e Administração',
         'Instituto Superior de Contabilidade e Administração da Universidade de Aveiro(ISCA)'),
        ('Universidade de Aveiro - Campus de Santiago',
         'Universidade de Aveiro - Campus de Santiago'),
    ]
    destino = models.CharField(max_length=255, choices=DESTINOS_CHOICES)
    origem_latitude = models.CharField(max_length=200, null=True)
    origem_longitude = models.CharField(max_length=200, null=True)
    destino_latitude = models.CharField(max_length=200, null=True)
    destino_longitude = models.CharField(max_length=200, null=True)
    vagas_disponiveis = models.PositiveBigIntegerField(validators=[MinValueValidator(1)])
    vagas_ocupadas = models.PositiveBigIntegerField(default=0)  # Novo campo

    data = models.DateField(default=timezone.now)
    hora = models.TimeField(default='00:00')

    def __str__(self):
        return f"{self.origem_latitude}, {self.origem_longitude} -> {self.destino_latitude}, {self.destino_longitude}"


    def __str__(self):
        return (
            f"Motorista: {self.driver_id.user.username}, "
            f"Origem: {self.origem}, "
            f"Destino: {self.destino}, "
            f"Data: {self.data}, "
            f"Hora: {self.hora}, "
            f"Vagas disponíveis: {self.vagas_disponiveis}"
            f"Vagas ocupadas: {self.vagas_ocupadas}"
        )
    
    @property
    def vagas_disponiveis_na_pagina_principal(self):
        return self.vagas_disponiveis - self.vagas_ocupadas
        
    @property
    def vagas_disponiveis_na_pagina_principal(self):
        return self.vagas_disponiveis - self.vagas_ocupadas
        
class PedidoBoleia(models.Model):
    boleia = models.ForeignKey(Boleia, on_delete=models.CASCADE)
    passageiro = models.ForeignKey(User, on_delete=models.CASCADE)
    aceito = models.BooleanField(null=True)
    data_pedido = models.DateTimeField(default=datetime.now)  # Adiciona este campo

    def __str__(self):
        return f'Pedido de {self.passageiro.username} para {self.boleia.origem}'

    def save(self, *args, **kwargs):
        if self.aceito:
            # Se o pedido for aceito, marque outros pedidos do mesmo passageiro como não aceitos
            PedidoBoleia.objects.filter(boleia=self.boleia, passageiro=self.passageiro).exclude(pk=self.pk).update(aceito=False)        
        super().save(*args, **kwargs)


class HistoricoBoleia(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    origem = models.CharField(max_length=255, null=True)
    destino = models.CharField(max_length=255, null=True)
    vagas_disponiveis = models.PositiveBigIntegerField(validators=[MinValueValidator(1)], null=True)
    vagas_ocupadas = models.PositiveBigIntegerField(default=0, null=True)
    data = models.DateField(default=timezone.now, null=True)
    hora = models.TimeField(default='00:00', null=True)

    cancelada = models.BooleanField(default=False)
    hora_chegada = models.TimeField(null=True, blank=True)

    def __str__(self):
        return (
            f"Usuário: {self.user.username}, "
            f"Origem: {self.origem}, "
            f"Destino: {self.destino}, "
            f"Data: {self.data}, "
            f"Hora: {self.hora}, "
            f"Vagas disponíveis: {self.vagas_disponiveis}, "
            f"Vagas ocupadas: {self.vagas_ocupadas}, "
            f"Cancelada: {self.cancelada}"
        )