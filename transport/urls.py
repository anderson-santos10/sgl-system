from django.urls import path
from .views import CenarioTransporteView

urlpatterns = [
    path("transport/", CenarioTransporteView.as_view(), name="transport_list"),
]
