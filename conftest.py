"""
Fichier de configuration pytest pour le projet mysite

Ce fichier configure automatiquement l'environnement Django pour les tests
"""
import os
import django
from pathlib import Path

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings.test')

# Setup Django
django.setup()

# Fixtures pytest globales (optionnel)
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def test_user():
    """Fixture pour créer un utilisateur de test"""
    user = User.objects.create_user(
        email='testuser@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User',
    )
    return user


@pytest.fixture
def authenticated_client(test_user):
    """Fixture pour un client API authentifié"""
    from rest_framework.test import APIClient
    from rest_framework.authtoken.models import Token

    client = APIClient()
    token, _ = Token.objects.get_or_create(user=test_user)
    client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    return client


@pytest.fixture
def api_client():
    """Fixture pour un client API non authentifié"""
    from rest_framework.test import APIClient
    return APIClient()
