from django.urls import path
from .views import CardView

urlpatterns = [
    path('', CardView.as_view(), name='dashboard_home'),
]
