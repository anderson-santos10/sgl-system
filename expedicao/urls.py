from django.urls import path
from .views import CenarioExpedicaoView, CenarioCardSeparacaoView, DetalheCard 

app_name = "expedicao"

urlpatterns = [
    path('cenario_expedicao/', CenarioExpedicaoView.as_view(), name = "cenario_expedicao"),
    path("cenario_card_separacao/<int:pk>/", CenarioCardSeparacaoView.as_view(), name="cenario_card_separacao"),
    path('detalhe/<int:pk>/', DetalheCard.as_view(), name = "detalhe_card"),

]
