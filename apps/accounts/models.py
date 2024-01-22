# import re
from django.db import models

'''
# Create your models here.
class Boleia(models.Model):
    origem = models.CharField(max_length=255)
    destino = models.CharField(max_length=255)
    frequencia = models.IntegerField()
    vagas_disponiveis = models.IntegerField()

class Driver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    car_name = models.CharField(max_length=255)  
    car_model = models.CharField(max_length=255, blank=True, null=True)
    car_year = models.PositiveIntegerField(blank=True, null=True)
    car_make = models.CharField(max_length=255, blank=True, null=True)
    car_license_plate = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.user.username if self.user else 'Driver sem usuário associado'

    class Meta:
        verbose_name = 'Motorista'

class Boleia(models.Model):
    driver_id = models.OneToOneField(Driver, on_delete=models.CASCADE, null=True, blank=True)
    origem = models.CharField(max_length=255) 
    destino = models.CharField(max_length=255) #colocar as opcoes disponiveis
    vagas_disponiveis = models.IntegerField()
    data = models.DateField(default='2024-01-01')
    hora = models.TimeField(default='00:00')

    def get_condutor_id(self):
        return self.driver_id.user.id

    def __str__(self):
        return (
            f"Motorista: {self.driver_id.user.username}, "
            f"Origem: {self.origem}, "
            f"Destino: {self.destino}, "
            f"Data: {self.data}, "
            f"Hora: {self.hora}, "
            f"Vagas disponíveis: {self.vagas_disponiveis}"
        )


class DescricaoUser(models.Model):
    descricao = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Para retoranar a descrição do user temos a seguinte função.
    def __str__(self):
        return f"Descrição do usuário: {self.descricao}"


class Reserva(models.Model):
    data_reserva = models.DateField()

    def __str__(self):
        return f"Data da reserva: {self.data_reserva}"


class ReservaBoleia(models.Model):
    """ Usado para vereficações futuras sobre se o utilizador
        está dentro de uma boleia, ativo, e assim não poder realizarum novo pedido de boleia, se tiver cancelado ou concluido
        pode realizar um novo pedido de boleia."""
    STATUS_CHOICES = (
        ('Ativo', 'Ativo'),
        ('Concluído', 'Concluído'),
        ('Cancelado', 'Cancelado')
    )
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE)
    boleia = models.ForeignKey(Boleia, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Ativo', null=True,
                              blank=True)
    """ Ele está prefinido como ativo mas pode aceitar como vazio ou nulo, porque uma pessoa pode não estar
     a realizar uma reserva necessariamente."""

    # Para sabermos como está o status da reserva boleia usamos a função seguinte que pode ser chamada.
    def __str__(self):
        return f"Estatuto da Viagem: {self.status}"

class TelemovelUser(models.Model):
    telemovel = models.CharField(max_length=20, default='000000000000')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Telemóvel do usuário: {self.telemovel}" \
            if self.telemovel \
            else 'Usuário sem telemóvel associado.'

class UtilizadorReserva(models.Model):
    utilizador = models.ForeignKey(User, on_delete=models.CASCADE)
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE)

class Notificacao(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    data = models.DateTimeField()
    mensagem = models.TextField()

    def __str__(self):
        return f"Mensagem: {self.mensagem}"

Aqui está criado o modelo para fazer o custom user para criar um admin e o modelo do user caso seja preciso uma nova tabela
para user por causa da verificação do email com a API.
 
class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password, nome, is_admin=False):
        if not email:
            raise ValueError('O campo email é obrigatório')
        if not nome:
            raise ValueError('O campo nome é obrigatório')
        if not username:
            raise ValueError('O campo username é obrigatório')

        # Verefica os caracteres especiais no nome e username que não podem ser usados
        if not nome or not re.match(r'^[A-Za-z0-9\s]+$', nome):
            raise ValueError('O nome deve conter caracteres alfanuméricos ou espaços, e não pode estar vazio ou conter apenas espaços.')
        if not username or not re.match(r'^[\w.@+-]+$', username):
            raise ValueError('O username deve conter caracteres alfanuméricos, underscore, ponto, arroba, sinal de adição ou hífen, e não pode estar vazio ou conter apenas espaços.')

        user = self.model(
            email=self.normalize_email(email),
            nome=nome,
            username=username,
            is_admin=is_admin
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password, nome):
        user = self.create_user(username, email, password, nome, is_admin=True)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=30, unique=True,
                                help_text="Este campo não pode conter caracteres especiais.")
    nome = models.CharField(max_length=255, help_text="Nome não pode conter caracteres especiais.")
    email = models.EmailField(unique=True, help_text="O email deve ser válido e conter '@'.")
    password = models.CharField(max_length=128, help_text="A password deve ser segura.")
    foto_perfil = models.URLField(blank=True, help_text="URL da foto de perfil.")
    is_admin = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'nome']

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        super(User, self).save(*args, **kwargs)'''