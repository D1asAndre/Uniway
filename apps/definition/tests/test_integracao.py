from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from apps.definition.models import UserProfile, Motorista
from apps.addboleia.models import Car
from faker import Faker

fake = Faker()

class UserProfileAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)

    def test_user_profile_api(self):
        # Crie um UserProfile para o usuário autenticado com dados fictícios
        data = {'photo': fake.image_url(), 'phone_number': fake.phone_number(), 'description': fake.text()}
        UserProfile.objects.create(user=self.user, **data)

        # Consulte o UserProfile usando a API
        url = reverse('user-profile-api')  # Certifique-se de substituir 'user-profile-api' pelo nome real da sua rota
        response = self.client.get(url)

        # Verifique se a resposta foi bem-sucedida (código 200)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Adicione mais asserções conforme necessário

    # Adicione mais testes para outros endpoints e modelos conforme necessário

class MotoristaAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)

    def test_motorista_api(self):
        # Crie um Motorista para o usuário autenticado com dados fictícios
        data = {'car_license': fake.word()}
        Motorista.objects.create(user_id=self.user, **data)

        # Consulte o Motorista usando a API
        url = reverse('motorista-api')  # Certifique-se de substituir 'motorista-api' pelo nome real da sua rota
        response = self.client.get(url)

        # Verifique se a resposta foi bem-sucedida (código 200)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Adicione mais asserções conforme necessário

    # Adicione mais testes para outros endpoints e modelos conforme necessário

class CarAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)

    def test_car_api(self):
        # Crie um Car para o usuário autenticado com dados fictícios
        data = {'car_model': fake.word(), 'car_year': fake.random_int(min=1880, max=2023),
                'car_make': fake.word(), 'car_license_plate': fake.word()}
        Car.objects.create(user=self.user, **data)

        # Consulte o Car usando a API
        url = reverse('car-api')  # Certifique-se de substituir 'car-api' pelo nome real da sua rota
        response = self.client.get(url)

        # Verifique se a resposta foi bem-sucedida (código 200)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Adicione mais asserções conforme necessário

    # Adicione mais testes para outros endpoints e modelos conforme necessário
