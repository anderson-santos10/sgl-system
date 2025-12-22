from django.db.models import Sum
from django.views.generic import ListView, CreateView, UpdateView
from django.shortcuts import render
from django.urls import reverse_lazy
from .models import NotaFiscal


def salvo_sucesso_view(request):
    return render(request, "receipt/sucesso.html")


class ReceiptListView(ListView):
    model = NotaFiscal
    ordering = ['-id']
    
    def get_queryset(self):
        queryset = super().get_queryset()

        # Captura filtros do GET
        data = self.request.GET.get('data')
        nf = self.request.GET.get('nf')
        tipo_veiculo = self.request.GET.get('tipo_veiculo')
        turno = self.request.GET.get('turno')
        un_origem = self.request.GET.get('un_origem')

        # Aplica filtros se existirem
        if data:
            queryset = queryset.filter(data=data)
        if nf:
            queryset = queryset.filter(nf__icontains=nf)
        if tipo_veiculo:
            queryset = queryset.filter(tipo_veiculo=tipo_veiculo)
        if turno:
            queryset = queryset.filter(turno=turno)
        if un_origem:
            queryset = queryset.filter(un_origem=un_origem)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['request'] = self.request  # mantém filtros selecionados no template
        return context


class ReceiptCreateView(CreateView):
    model = NotaFiscal
    fields = ["turno", "nf", "un_origem", "qnt_pallet", "tipo_veiculo", "peso_nota"]
    success_url = reverse_lazy('salvo_sucesso')
    
    
class NotasUpdateView(UpdateView):
    model = NotaFiscal
    fields = ["turno", "nf", "un_origem", "qnt_pallet", "tipo_veiculo", "peso_nota"]
    success_url = reverse_lazy('salvo_sucesso')