#mysite/urls.py
#----

from django.contrib import admin
from django.urls import include, path


urlpatterns = [
	path('idarast/', admin.site.urls),

	path('api/accounts/', include('authemail.urls')),
	path('api/stages/', include('stages.urls')),
	path('api/aos/', include('aos.urls')),
	path('api/omra/', include('omra.urls')),
	path('api/ovs/', include('ovs.urls')),
]