#mysite/urls.py
#----
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
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

# Servir les fichiers media et static en développement (AVANT que l'admin catch-all ne les capture)
if settings.DEBUG:
	urlpatterns = [
		*static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
		*static(settings.STATIC_URL, document_root=settings.STATIC_ROOT),
		*urlpatterns,
	]
