#mysite/urls.py
#----
from django.contrib import admin
from django.urls import include, path
from fournisseurs.admin.facture_admin import fournisseur_admin

urlpatterns = [
    # URL de l'admin personnalisé pour les fournisseurs
    path('admin/fournisseurs/', fournisseur_admin.urls),

	path('admin/', admin.site.urls),

	path('api/accounts/', include('authemail.urls')),
	path('api/stages/', include('stages.urls')),
	path('api/aos/', include('aos.urls')),
	path('api/omra/', include('omra.urls')),
	path('api/fournisseurs/', include('fournisseurs.urls')),
]
