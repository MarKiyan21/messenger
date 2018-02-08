from django.conf.urls import url, include
from project import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'', include('messenger.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_URL)
