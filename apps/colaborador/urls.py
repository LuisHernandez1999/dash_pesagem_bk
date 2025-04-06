from django.urls import path
from .views import criar_colaborador

urlpatterns = [
    path('colaborador/criar/', criar_colaborador, name='criar_colaborador'),
]
