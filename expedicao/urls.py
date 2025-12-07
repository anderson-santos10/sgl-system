from django.urls import path
from expedicao import views
from .views import (
    ControleSeparacaoCreateView, 
    CargasListView,
    CargaUpdateView,
    CargaDeleteView,
    CargasConcluidasView,
    TransporteViews,
    TransporteUpdateView,
    concluir_carga
)


app_name = "expedicao"

urlpatterns = [
    path("home/", views.home, name="home"),
    path("controle-separacao/", ControleSeparacaoCreateView.as_view(), name="controle_separacao"),
    path("cargas/", CargasListView.as_view(), name="cargas_list"),
    path("carga/<int:pk>/editar/", CargaUpdateView.as_view(), name="editar_carga"),
    path("carga/<int:pk>/excluir/", CargaDeleteView.as_view(), name="excluir_carga"),
    path("carga/<int:pk>/concluir/", concluir_carga, name="concluir_carga"),
    path('carga/<int:pk>/', views.CargaDetailView.as_view(), name='detalhe_carga'),
    path('cargas-concluidas/', CargasConcluidasView.as_view(), name='cargas_concluidas'),
    path('cenario_transporte/', TransporteViews.as_view(), name = "cenario_transporte"),
    path("editar_transporte/<int:pk>/", TransporteUpdateView.as_view(), name="editar_transporte"),
    path('carga/inserir/', views.InserirCargaView.as_view(), name='inserir_carga'),


]
