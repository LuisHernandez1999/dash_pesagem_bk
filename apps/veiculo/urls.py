from django.urls import path
from .views import criar_veiculo

urlpatterns = [
    path('veiculos/criar/', criar_veiculo, name='criar_veiculo'),
]
