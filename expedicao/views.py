from itertools import count
from django import forms
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.timezone import now
from .models import ControleSeparacao

# ---------- CONSTANTES ----------
TIPOS_VEICULO = ["3/4", "toco", "carreta",
                 "truck", "rodotrem", "container", "utilitario"]

# ---------- FUNÇÕES AUXILIARES ----------


def preencher_campos_padrao(instance):
    """
    Preenche campos obrigatórios com valores padrão caso estejam vazios.
    """
    defaults = {
        "entrega_box": "Não informado",
        "tipo_veiculo": "Não informado",
        "outros_separadores": "Não informado",
        "conferente": "Não informado",
    }
    for field, value in defaults.items():
        if not getattr(instance, field):
            setattr(instance, field, value)


class CargaForm(forms.ModelForm):
    class Meta:
        model = ControleSeparacao
        fields = ['lecom', 'numero_transporte', 'seg', 'tipo_veiculo',
                  'destino', 'uf', 'peso', 'm3', 'observacao']
        widgets = {
            'lecom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lecom'}),
            'cargas': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Número de Cargas'}),
            'seg': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Segmento'}),
            'tipo_veiculo': forms.Select(attrs={'class': 'form-select'}),
            'destino': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Destino'}),
            'uf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'UF'}),
            'peso': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Peso (Kg)'}),
            'm3': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'M³'}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Observação', 'rows': 3}),
        }


class InserirCargaView(CreateView):
    model = ControleSeparacao
    form_class = CargaForm
    template_name = 'expedicao/form_transporte.html'
    # volta pra tabela depois de salvar
    success_url = reverse_lazy('expedicao:cenario_transporte')

    def form_valid(self, form):
        return super().form_valid(form)


class CargasAgrupadasPorVeiculoView(ListView):
    model = ControleSeparacao
    template_name = "expedicao/cargas_agrupadas.html"
    context_object_name = "grupos"

    def get_queryset(self):
        return (
            ControleSeparacao.objects
            .values("tipo_veiculo")
            .annotate(total=count("id"))
            .order_by("tipo_veiculo")
        )

# ---------- HOME ----------


@login_required
def home(request):
    return render(request, "home.html")

# ---------- CREATE ----------


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
        self.object = form.save(commit=False)
        preencher_campos_padrao(self.object)
        self.object.save()
        messages.success(self.request, "Carga criada com sucesso!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipos_veiculo'] = TIPOS_VEICULO
        return context

# ---------- DETAIL ----------


class CargaDetailView(DetailView):
    model = ControleSeparacao
    template_name = 'expedicao/detalhe_carga.html'
    context_object_name = 'carga'

# ---------- LIST ----------


class CargasListView(ListView):
    model = ControleSeparacao
    template_name = "expedicao/card_separacao.html"
    context_object_name = 'cargas'
    ordering = ['-id']

    def get_queryset(self):
        queryset = super().get_queryset()
        numero_transporte = self.request.GET.get('numero_transporte')
        status = self.request.GET.get('status')

        if numero_transporte:
            queryset = queryset.filter(
                numero_transporte__icontains=numero_transporte)
        if status:
            queryset = queryset.filter(status=status)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['numero_transporte_search'] = self.request.GET.get(
            'numero_transporte', '')
        context['status_selected'] = self.request.GET.get('status', '')
        return context

# ---------- LIST CONCLUÍDAS ----------


class CargasConcluidasView(ListView):
    model = ControleSeparacao
    template_name = "expedicao/cargas_concluidas.html"
    context_object_name = "cargas"

    def get_queryset(self):
        queryset = ControleSeparacao.objects.filter(status="Concluido")
        filters = {
            "data__day": self.request.GET.get("day"),
            "data__month": self.request.GET.get("month"),
            "data__year": self.request.GET.get("year"),
        }
        filters = {k: v for k, v in filters.items() if v}
        if filters:
            queryset = queryset.filter(**filters)

        return queryset.order_by('-data')

# ---------- UPDATE TRANSPORTE ----------


class TransporteUpdateView(UpdateView):
    model = ControleSeparacao
    template_name = "expedicao/editar_transporte.html"
    fields = [
        'lecom', 'resumo', 'entregas', 'tipo_veiculo', 'destino',
        'uf', 'peso', 'm3', 'data', 'entrega_box', 'mod', 'observacao'
    ]
    success_url = reverse_lazy('expedicao:cenario_transporte')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipos_veiculo'] = TIPOS_VEICULO
        return context

    def form_valid(self, form):
        preencher_campos_padrao(form.instance)
        messages.success(self.request, "Transporte atualizado com sucesso!")
        return super().form_valid(form)

# ---------- UPDATE CARGA ----------


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
        context['tipos_veiculo'] = TIPOS_VEICULO
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        preencher_campos_padrao(self.object)
        # Reset status ao editar
        self.object.status = "Pendente"
        self.object.finalizado = False
        self.object.save()
        messages.success(self.request, "Carga atualizada com sucesso!")
        return super().form_valid(form)

# ---------- DELETE ----------


class CargaDeleteView(DeleteView):
    model = ControleSeparacao
    template_name = "expedicao/carga_confirm_delete.html"
    success_url = reverse_lazy('expedicao:cargas_list')

# ---------- LIST TRANSPORTE ----------


class TransporteViews(ListView):
    model = ControleSeparacao
    template_name = "expedicao/cenario_transporte.html"
    context_object_name = 'cargas'

# ---------- FUNÇÃO CONCLUIR ----------


def concluir_carga(request, pk):
    carga = get_object_or_404(ControleSeparacao, pk=pk)
    preencher_campos_padrao(carga)
    carga.finalizado = True
    carga.save()
    messages.success(request, "Carga concluída com sucesso!")
    return redirect("expedicao:cargas_list")
