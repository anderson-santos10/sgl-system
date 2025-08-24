from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from django.contrib.auth.decorators import login_required
from .models import ControleSeparacao
from django.utils.timezone import now

# Função auxiliar para preencher campos vazios
def preencher_campos_padrao(instance):
    if not instance.entrega_box:
        instance.entrega_box = "Não informado"
    if not instance.tipo_veiculo:
        instance.tipo_veiculo = "Não informado"
    if not instance.outros_separadores:
        instance.outros_separadores = "Não informado"
    if not instance.conferente:
        instance.conferente = "Não informado"
        
@login_required
def home(request):
    return render(request, "home.html")

# Criar uma nova carga
TIPOS_VEICULO = ["3/4","toco","carreta","truck","rodotrem","container","utilitario"]

class ControleSeparacaoCreateView(CreateView):
    model = ControleSeparacao
    template_name = "expedicao/controle-separacao.html"
    fields = [
        'data', 'destino', 'numero_transporte', 'ot', 'entrega_box', 'tipo_veiculo',
        'outros_separadores', 'conferente', 'inicio_separacao',
        'resumo_conf', 'resumo_motorista', 'etiquetas_cds', 'carga_gerada',
        'atribuida', 'finalizado'
    ]
    success_url = reverse_lazy('expedicao:cargas_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        preencher_campos_padrao(self.object)
        self.object.save()
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipos_veiculo'] = TIPOS_VEICULO
        return context
    
    
class CargaDetailView(DetailView):
    model = ControleSeparacao
    template_name = 'expedicao/detalhe_carga.html'
    context_object_name = 'carga'


# Listar cargas em cards
class CargasListView(ListView):
    model = ControleSeparacao
    template_name = "expedicao/card_separacao.html"
    context_object_name = 'cargas'
    ordering = ['-id']
    
    def post(self, request, *args, **kwargs):
        carga_id = request.POST.get('carga_id')
        if carga_id:
            carga = get_object_or_404(ControleSeparacao, pk=carga_id)
            # Ciclo de status
            if carga.status == "Pendente":
                carga.status = "Andamento"
            elif carga.status == "Andamento":
                carga.status = "Concluido"
            carga.save()
        return redirect('expedicao:cargas_list')
    
    def get_queryset(self):
        queryset = super().get_queryset()

        # Filtrar por status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        # Filtrar por número de transporte
        numero_transporte = self.request.GET.get('numero_transporte')
        if numero_transporte:
            queryset = queryset.filter(numero_transporte__icontains=numero_transporte)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Para manter os filtros no template
        context['status_selected'] = self.request.GET.get('status', '')
        context['numero_transporte_search'] = self.request.GET.get('numero_transporte', '')
        
        return context
    
    
class CargasConcluidasView(ListView):
    model = ControleSeparacao
    template_name = "expedicao/cargas_concluidas.html"  # template exclusivo
    context_object_name = "cargas"

    def get_queryset(self):
        hoje = now()
        return ControleSeparacao.objects.filter(
            status="Concluido",
            data__month=hoje.month,
            data__year=hoje.year
        ).order_by('-data')
        
    def get_queryset(self):
        queryset = ControleSeparacao.objects.filter(status="Concluido")
        day = self.request.GET.get("day")
        month = self.request.GET.get("month")
        year = self.request.GET.get("year")

        if day:
            queryset = queryset.filter(data__day=day)
        if month:
            queryset = queryset.filter(data__month=month)
        if year:
            queryset = queryset.filter(data__year=year)

        return queryset.order_by('-data')

# Editar carga
class CargaUpdateView(UpdateView):
    model = ControleSeparacao
    template_name = "expedicao/controle-separacao.html"
    fields = [
        'data', 'destino', 'numero_transporte', 'ot', 'entrega_box', 'tipo_veiculo',
        'outros_separadores', 'conferente', 'inicio_separacao',
        'resumo_conf', 'resumo_motorista', 'etiquetas_cds', 'carga_gerada',
        'atribuida', 'finalizado'
    ]
    success_url = reverse_lazy('expedicao:cargas_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Aqui você define os tipos de veículos
        context['tipos_veiculo'] = TIPOS_VEICULO
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        preencher_campos_padrao(self.object)
        
        # Resetar status para Pendente ao editar
        self.object.status = "Pendente"
        # Se a carga estava marcada como finalizada, desfaz
        self.object.finalizado = False
        
        self.object.save()
        return response


# Excluir carga
class CargaDeleteView(DeleteView):
    model = ControleSeparacao
    template_name = "expedicao/carga_confirm_delete.html"
    success_url = reverse_lazy('expedicao:cargas_list')


# Concluir carga
def concluir_carga(request, pk):
    carga = get_object_or_404(ControleSeparacao, pk=pk)
    carga.finalizado = True
    preencher_campos_padrao(carga)
    carga.save()
    return redirect("expedicao:cargas_list")
