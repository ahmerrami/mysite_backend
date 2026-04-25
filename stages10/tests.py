from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from stages10.models import Candidat

class SendSmsCodeTest(APITestCase):
    def setUp(self):
        self.candidat_data = {
            "civilite": "M.",
            "nom": "Testeur",
            "prenom": "Jean",
            "cin": "AB123456",
            "date_naissance": "2000-01-01",
            "telephone": "+212660147499",
            "email": "ahmederrami@gamil.com",
            "adresse": "1 rue de test",
            "ville": 1  # Assurez-vous qu'une ville avec id=1 existe
        }
        # Créer un candidat
        response = self.client.post("/api/stages10/candidats/", self.candidat_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.candidat_id = response.data["id"]

    def test_send_sms_code(self):
        url = f"/api/stages10/candidats/{self.candidat_id}/send_sms_code/"
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("detail", response.data)
        self.assertTrue("Code envoyé" in response.data["detail"])
