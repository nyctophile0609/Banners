from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('api/auth/',obtain_auth_token),
    path('not_meant_for_you/', admin.site.urls),
    path('api/',include('api.urls'))
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
