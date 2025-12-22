from django.urls import path
from receipt.views import DashboardView


urlpatterns = [
   path("cards/", DashboardView.as_view(), name="cards"),
]