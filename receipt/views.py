from datetime import timezone
from django.db.models import Sum
from django.views.generic import ListView, CreateView, UpdateView, TemplateView
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
    
class DashboardReceiptView(TemplateView):
    template_name = "/dashboard/home.html"  

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        hoje = timezone.localdate()
        notas_qs = NotaFiscal.objects.all()

        # Total de notas
        context['notas'] = notas_qs.count()

        # Total por UN
        context['un10'] = notas_qs.filter(un_origem="10").count()
        context['un20'] = notas_qs.filter(un_origem="20").count()
        context['un40'] = notas_qs.filter(un_origem="40").count()

        # Total de pallets
        total_pallets = notas_qs.aggregate(total=Sum('qnt_pallet'))['total'] or 0
        context['total'] = total_pallets

        # Total peso bruto
        total_peso = notas_qs.aggregate(total=Sum('peso_nota'))['total'] or 0
        context['total_peso'] = total_peso

        # Data de hoje
        context['hoje'] = hoje.strftime("%d/%m/%Y")

        return context