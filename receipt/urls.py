from django.urls import path
from .views import ReceiptListView, ReceiptCreateView,  salvo_sucesso_view

urlpatterns = [
    path("", ReceiptListView.as_view(), name="index"),
    path("notas/", ReceiptListView.as_view(), name="notas_list"),
    path("create/", ReceiptCreateView.as_view(), name="create_list"),
    path("sucesso/", salvo_sucesso_view, name="salvo_sucesso"),
]

