from django.urls import path
from . import views

urlpatterns = [
    path('criar-pesagem/', views.criar_pesagem, name='criar_pesagem'),
    path('pesagens-por-mes/', views.exibir_pesagem_por_mes, name='exibir_pesagem_por_mes'),
    path('meta-batida/', views.meta_batida, name='meta_batida'),
    path('ranking-motoristas/', views.ranking_motoristas_com_maiores_pesagens, name='ranking_motoristas'),
    path('ranking-cooperativas/', views.ranking_cooperativas_com_maiores_pesagens, name='ranking_cooperativas'),
    path('media-peso-cooperativa/', views.media_peso_por_cooperativa, name='media_peso_cooperativa'),
    path('eficiencia-motoristas/', views.eficiencia_por_motorista, name='eficiencia_motoristas'),
    path('tipos-pesagem-frequentes/', views.tipos_pesagem_mais_frequentes, name='tipos_pesagem_frequentes'),
]
