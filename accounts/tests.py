"""
Exemple de tests pour l'application accounts
Remplacez ce fichier par vos vrais tests
"""
import pytest
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status

User = get_user_model()


class UserModelTests(TestCase):
    """Tests pour le modèle utilisateur"""

    def setUp(self):
        """Préparation avant chaque test"""
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'John',
            'last_name': 'Doe',
        }

    def test_user_creation(self):
        """Test la création d'un utilisateur"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.email, self.user_data['email'])
        self.assertTrue(user.check_password(self.user_data['password']))

    def test_user_str(self):
        """Test la représentation string de l'utilisateur"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), self.user_data['email'])


@pytest.mark.django_db
class TestUserAPI:
    """Tests API pour les utilisateurs avec pytest"""

    def test_user_list(self):
        """Test l'accès à la liste des utilisateurs"""
        client = APIClient()
        # Vous pouvez ajouter vos tests API ici
        # response = client.get(reverse('user-list'))
        # assert response.status_code == 200

    def test_user_create(self):
        """Test la création d'un utilisateur via l'API"""
        client = APIClient()
        user_data = {
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'first_name': 'Jane',
            'last_name': 'Smith',
        }
        # response = client.post(reverse('user-list'), user_data, format='json')
        # assert response.status_code == 201


class AuthenticationTests(APITestCase):
    """Tests pour l'authentification"""

    def setUp(self):
        """Préparation avant chaque test"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='auth@example.com',
            password='testpass123',
        )

    def test_user_authentication(self):
        """Test l'authentification d'un utilisateur"""
        # Exemple de test d'authentification
        self.assertTrue(self.user.is_active)

    def test_invalid_password(self):
        """Test l'authentification avec un mauvais mot de passe"""
        user = User.objects.get(email='auth@example.com')
        self.assertFalse(user.check_password('wrongpassword'))


# Ajoutez vos propres tests ci-dessous
class YourCustomTests(TestCase):
    """Remplacez par vos tests personnalisés"""

    def test_example(self):
        """Exemple de test simple"""
        self.assertEqual(1 + 1, 2)
