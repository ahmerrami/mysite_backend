#mysite/urls.py
#----

from django.contrib import admin
from django.urls import include, path


urlpatterns = [
	path('idarast/', admin.site.urls),

	path('api/accounts/', include('authemail.urls')),
	path('api/stages/', include('stages.urls')),
]