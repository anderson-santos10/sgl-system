from django.urls import path
from expedicao import views
from .views import CenarioExpedicaoView

app_name = "expedicao"

urlpatterns = [
    path('cenario_expedicao/', CenarioExpedicaoView.as_view(), name = "cenario_expedicao"),
]
