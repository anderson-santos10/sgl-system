from django.db.models import Sum
from datetime import date
from django.views.generic import ListView, CreateView, UpdateView
from django.shortcuts import render
from django.urls import reverse_lazy
from .models import NotaFiscal
from django.views import View


def salvo_sucesso_view(request):
    return render(request, "receipt/sucesso.html")

class DashboardView(View):
    def get(self, request):
        hoje = date.today()

        # Filtra somente notas do dia
        notas_hoje = NotaFiscal.objects.filter(data=hoje)
        notas = notas_hoje.count()
        
        # Quantidade de pallets por unidade
        total_peso = notas_hoje.aggregate(total_peso=Sum('peso_nota'))['total_peso'] or 0
        un10 = notas_hoje.filter(un_origem="UN10").aggregate(Sum("qnt_pallet"))["qnt_pallet__sum"] or 0
        un20 = notas_hoje.filter(un_origem="UN20").aggregate(Sum("qnt_pallet"))["qnt_pallet__sum"] or 0
        un40 = notas_hoje.filter(un_origem="UN40").aggregate(Sum("qnt_pallet"))["qnt_pallet__sum"] or 0
        
        # Total
        total = un10 + un20 + un40

        context = {
            "total_peso": total_peso,
            "notas": notas,
            "hoje": hoje,
            "un10": un10,
            "un20": un20,
            "un40": un40,
            "total": total,
        }

        return render(request, "home.html", context)


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


class ControleSeparacaoView(CreateView):
    template_name = "expedicao/controle_separacao.html"
    model = NotaFiscal
    fields = ["data", "turno", "nf", "un_origem", "qnt_pallet", "tipo_veiculo", "peso_nota"]
    
class CardsView(View):
    def get(self, request):
        ex = NotaFiscal.objects.all().order_by('-id')  # pega todas as cargas do maior para o menor
        return render(request, 'expedicao/cards.html', {'ex': ex})

class ListaCargasView(ListView):
    template_name = "expedicao/lista_cargas.html"
    model = NotaFiscal
    
class NotasUpdateView(UpdateView):
    model = NotaFiscal
    fields = ["turno", "nf", "un_origem", "qnt_pallet", "tipo_veiculo", "peso_nota"]
    success_url = reverse_lazy('salvo_sucesso')