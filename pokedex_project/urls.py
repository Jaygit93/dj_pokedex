from django.contrib import admin
from django.urls import path
from pokedex.views import pokemon_list, pokemon_detail
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', pokemon_list, name='pokemon_list'),
    path('pokemon/<int:pok_id>/', pokemon_detail, name='pokemon_detail'),
]   + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
