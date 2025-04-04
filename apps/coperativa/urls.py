from django.urls import path
from .views import criar_cooperativa

urlpatterns = [
    path('cooperativas/criar/', criar_cooperativa, name='criar_cooperativa'),
]
