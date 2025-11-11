#mysite/urls.py
#----
from django.contrib import admin
from django.urls import include, path
from fournisseurs.admin.facture_admin import fournisseur_admin

urlpatterns = [
	# URLs API et applications (doivent être avant l'admin à la racine)
	
	# API endpoints désactivées pour sécurité (non utilisées par le frontend)
	# path('api/accounts/', include('authemail.urls')),
	
	# API endpoints actifs (utilisés par mysite_frontend)
	path('api/stages/', include('stages.urls')),
	path('api/aos/', include('aos.urls')),
	path('api/omra/', include('omra.urls')),
	
	# API endpoints AJAX pour l'administration (utilisés par les fichiers .js)
	path('api/fournisseurs/', include('fournisseurs.urls')),
	
	# URLs pour l'authentification et reset password
	path('accounts/', include('accounts.urls')),
	
    # Admin personnalisé pour les fournisseurs
    path('fournisseurs/', fournisseur_admin.urls),

	# Admin Django standard à la racine (doit être en dernier)
	path('', admin.site.urls),
]
