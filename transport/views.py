from datetime import date
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, UpdateView
from django.contrib import messages
from decimal import Decimal, InvalidOperation
from django.db import transaction
from django.utils.dateparse import parse_date
from .models import Lecom, Carga, Entrega, Veiculo



class CriarTransporteView(View):
    template_name = "transport/inserir_carga.html"

    def get(self, request):
        # Apenas exibe a página com o formulário
        return render(request, self.template_name)

    def post(self, request):
        # Quando o usuário envia o formulário, cai aqui
        return self.salvar_dados(request)

    def salvar_dados(self, request):

        # -------------------------------
        # 1️⃣ CAPTURA DADOS DA LECOM
        # -------------------------------
        lecom_code = request.POST.get("lecom", "").strip()
        destino = request.POST.get("destino", "").strip()
        uf = request.POST.get("uf", "").strip()
        peso_raw = request.POST.get("peso", "0").strip()
        m3_raw = request.POST.get("m3", "0").strip()
        data_raw = request.POST.get("data", "").strip()
        observacao = request.POST.get("observacao", "").strip()

        errors = []

        # Validação simples
        if not lecom_code:
            errors.append("O campo LECOM é obrigatório.")
        if not destino:
            errors.append("O campo Destino é obrigatório.")
        if not uf:
            errors.append("O campo UF é obrigatório.")

        # Converte peso
        try:
            peso = Decimal(peso_raw)
        except InvalidOperation:
            errors.append("Peso inválido.")
            peso = Decimal("0")

        # Converte m3
        try:
            m3 = Decimal(m3_raw)
        except InvalidOperation:
            errors.append("m³ inválido.")
            m3 = Decimal("0")

        # Converte data
        data = parse_date(data_raw)
        if data is None:
            errors.append("Data inválida. Use YYYY-MM-DD.")

        # Se tiver erros → volta
        if errors:
            for e in errors:
                messages.error(request, e)
            return redirect("transport:cenario_transporte")


        # ----------------------------------
        # 2️⃣ CAPTURA DADOS DO VEÍCULO
        # ----------------------------------
        tipo_veiculo = request.POST.get("tipo_veiculo", "Não informado")

        # ----------------------------------
        # 3️⃣ CAPTURA LISTA DE CARGAS
        # ----------------------------------
        # Estes campos devem vir como listas no formulário
        cargas_list = request.POST.getlist("carga[]")
        seq_list = request.POST.getlist("seq[]")
        total_entregas_list = request.POST.getlist("total_entregas[]")
        mod_list = request.POST.getlist("mod[]")

        # Consistência
        if not cargas_list:
            messages.error(request, "É necessário informar ao menos uma carga.")
            return redirect("transport:cenario_transporte")


        # ----------------------------------
        # 4️⃣ CAPTURA LISTA DE ENTREGAS (opcional)
        # ----------------------------------
        # entrega_carga_ref[] indica a qual carga a entrega pertence
        entrega_numeros = request.POST.getlist("entrega_numero[]")
        entrega_carga_ref = request.POST.getlist("entrega_carga_index[]")

        # ----------------------------------
        # 5️⃣ SALVA TUDO NO BANCO COM TRANSACTION
        # ----------------------------------
        try:
            with transaction.atomic():

                # Salva LECOM
                lecom = Lecom.objects.create(
                    lecom=lecom_code,
                    destino=destino,
                    uf=uf,
                    peso=peso,
                    m3=m3,
                    data=data,
                    observacao=observacao,
                )

                # Salva veículo (OneToOne)
                Veiculo.objects.create(
                    lecom=lecom,
                    tipo_veiculo=tipo_veiculo
                )

                # Salvar cada carga associada à LECOM
                cargas_salvas = []

                for i, carga_num in enumerate(cargas_list):
                    carga_obj = Carga.objects.create(
                        lecom=lecom,
                        carga=carga_num,
                        seq=seq_list[i] if seq_list else None,
                        total_entregas=total_entregas_list[i] if total_entregas_list else "1",
                        mod=mod_list[i] if mod_list else "",
                    )
                    cargas_salvas.append(carga_obj)

                # Salvar as entregas de cada carga
                for idx, numero_entrega in enumerate(entrega_numeros):
                    if numero_entrega.strip() == "":
                        continue

                    indice_carga = int(entrega_carga_ref[idx])
                    carga_relacionada = cargas_salvas[indice_carga]

                    Entrega.objects.create(
                        numero=numero_entrega,
                        carga=carga_relacionada
                    )

        except Exception as e:
            messages.error(request, f"Erro ao salvar dados: {e}")
            return redirect("transport:cenario_transporte")


        # Sucesso
        messages.success(request, f"LECOM {lecom.lecom} criada com sucesso.")
        return redirect("transport:cenario_transporte")

class CenarioTransporteView(ListView):
    model = Lecom
    template_name = "transport/cenario_transporte.html"
    context_object_name = "lecoms"
    ordering = ["-id"]

    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related("cargas", "veiculo")

        # FILTROS
        transporte_id = self.request.GET.get("transporte_id")
        lecom = self.request.GET.get("lecom")
        status = self.request.GET.get("status")

        if transporte_id and transporte_id.isdigit():
            queryset = queryset.filter(id=int(transporte_id))

        if lecom:
            queryset = queryset.filter(lecom__icontains=lecom)

        if status in ["LIBERADO", "BLOQUEADO"]:
            queryset = queryset.filter(status=status)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        grupo_cargas = []
        for lecom in context["lecoms"]:
            grupo_cargas.append({
                "grupo": lecom,
                "cargas": lecom.cargas.all().order_by("seq")
            })

        context["grupo_cargas"] = grupo_cargas
        context["total_lecoms"] = context["lecoms"].count()

        # Mantém os valores dos filtros no template
        context["filtro_transporte_id"] = self.request.GET.get("transporte_id", "")
        context["filtro_lecom"] = self.request.GET.get("lecom", "")
        context["filtro_status"] = self.request.GET.get("status", "")

        return context

class EditarTransporteView(View):
    template_name = "transport/inserir_carga.html"
    success_url = reverse_lazy("transport:cenario_transporte")

    def get(self, request, pk):
        lecom = get_object_or_404(Lecom, pk=pk)
        cargas = lecom.cargas.all()
        return render(request, self.template_name, {
            "lecom": lecom,
            "cargas": cargas,
            "modo_edicao": True
        })

    def post(self, request, pk):
        lecom = get_object_or_404(Lecom, pk=pk)

        # Atualiza os campos do Lecom
        lecom.lecom = request.POST.get("lecom")
        lecom.destino = request.POST.get("destino")
        lecom.uf = request.POST.get("uf")
        lecom.data = request.POST.get("data")
        lecom.peso = request.POST.get("peso") or 0
        lecom.m3 = request.POST.get("m3") or 0
        lecom.observacao = request.POST.get("observacao")
        lecom.status = request.POST.get("status", "BLOQUEADO")
        lecom.save()

        # Atualiza as cargas existentes
        carga_ids = request.POST.getlist("carga_id[]")
        carga_nomes = request.POST.getlist("carga[]")
        seqs = request.POST.getlist("seq[]")
        total_entregas_list = request.POST.getlist("total_entregas[]")
        mods = request.POST.getlist("mod[]")

        for i, cid in enumerate(carga_ids):
            carga = get_object_or_404(Carga, pk=cid)
            carga.carga = carga_nomes[i]
            carga.seq = seqs[i] or 1
            carga.total_entregas = total_entregas_list[i] or "1"
            carga.mod = mods[i] or "-"
            carga.save()

        return redirect(self.success_url)
    
class DashboardView(View):
    def get(self, request):
        hoje = date.today()

        # Filtra somente notas do dia
        lecom_hoje = Lecom.objects.filter(data=hoje)
        lecoms = lecom_hoje.count()
        lecoms+=1
        
        context = {
            "total_lecoms": lecoms
        }

        return render(request, "dashboard/home.html", context)


    