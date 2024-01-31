from django.test import TestCase
from apps.definition.models import UserProfile, Motorista
from apps.addboleia.models import Car
from apps.definition.api.serializers import UserProfileSerializer, MotoristaSerializer, CarSerializer
from faker import Faker

fake = Faker()

class UserProfileSerializerTest(TestCase):
    def test_validate_phone_number_valid(self):
        data = {'phone_number': fake.phone_number()}
        serializer = UserProfileSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_validate_phone_number_invalid(self):
        data = {'phone_number': 'invalid'}
        serializer = UserProfileSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('phone_number', serializer.errors)

    def test_validate_description_valid(self):
        data = {'description': fake.text(max_nb_chars=100)}
        serializer = UserProfileSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_validate_description_invalid(self):
        data = {'description': 'A' * 101}
        serializer = UserProfileSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('description', serializer.errors)

    # Adicione mais testes conforme necessário
