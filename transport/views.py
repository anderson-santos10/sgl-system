from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView
from django.contrib import messages
from decimal import Decimal, InvalidOperation
from django.db import transaction
from django.utils.dateparse import parse_date
from .models import Lecom, Carga, Entrega, Veiculo
from expedicao.models import ControleSeparacao


class CriarTransporteView(View):
    template_name = "transport/inserir_carga.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):

        # -------------------------------
        # 1️⃣ DADOS DA LECOM
        # -------------------------------
        lecom_code = request.POST.get("lecom", "").strip()
        destino = request.POST.get("destino", "").strip()
        uf = request.POST.get("uf", "").strip()
        peso_raw = request.POST.get("peso", "0").strip()
        m3_raw = request.POST.get("m3", "0").strip()
        data_raw = request.POST.get("data", "").strip()
        observacao = request.POST.get("observacao", "").strip()

        errors = []

        if not lecom_code:
            errors.append("O campo LECOM é obrigatório.")
        if not destino:
            errors.append("O campo Destino é obrigatório.")
        if not uf:
            errors.append("O campo UF é obrigatório.")

        peso_raw = request.POST.get("peso", "").strip()
        m3_raw = request.POST.get("m3", "").strip()

        try:
            peso = Decimal(peso_raw) if peso_raw else Decimal("0.00")
        except InvalidOperation:
            peso = Decimal("0.00")

        try:
            m3 = Decimal(m3_raw) if m3_raw else Decimal("0.00")
        except InvalidOperation:
            m3 = Decimal("0.00")


        data = parse_date(data_raw)
        if not data:
            errors.append("Data inválida.")

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, self.template_name)

        # 🚫 LECOM DUPLICADA (ANTES DA TRANSACTION)
        if Lecom.objects.filter(lecom=lecom_code).exists():
            messages.error(request, "Esse Numero de LECOM já existe.")
            return render(request, self.template_name)

        # -------------------------------
        # 2️⃣ VEÍCULO
        # -------------------------------
        tipo_veiculo = request.POST.get("tipo_veiculo", "Não informado")

        # -------------------------------
        # 3️⃣ CARGAS
        # -------------------------------
        cargas_list = request.POST.getlist("carga[]")
        seq_list = request.POST.getlist("seq[]")
        total_entregas_list = request.POST.getlist("total_entregas[]")
        mod_list = request.POST.getlist("mod[]")

        if not cargas_list:
            messages.error(request, "Informe ao menos uma carga.")
            return render(request, self.template_name)

        # -------------------------------
        # 4️⃣ ENTREGAS
        # -------------------------------
        entrega_numeros = request.POST.getlist("entrega_numero[]")
        entrega_carga_ref = request.POST.getlist("entrega_carga_index[]")

        # -------------------------------
        # 5️⃣ SALVAR TUDO
        # -------------------------------
        try:
            with transaction.atomic():

                # 🔹 LECOM
                lecom = Lecom.objects.create(
                    lecom=lecom_code,
                    destino=destino,
                    uf=uf,
                    peso=peso,
                    m3=m3,
                    data=data,
                    observacao=observacao,
                )

                # 🔹 VEÍCULO
                Veiculo.objects.create(
                    lecom=lecom,
                    tipo_veiculo=tipo_veiculo
                )

                # 🔹 CARGAS
                cargas_salvas = []

                for i, carga_num in enumerate(cargas_list):

                    # 🚫 CARGA DUPLICADA NA MESMA LECOM
                    if Carga.objects.filter(lecom=lecom, carga=carga_num).exists():
                        messages.error(
                            request,
                            f"A carga {carga_num} já existe para este LECOM."
                        )
                        raise ValueError("Carga duplicada")

                    carga_obj = Carga.objects.create(
                        lecom=lecom,
                        carga=carga_num,
                        seq=seq_list[i] if seq_list else 1,
                        total_entregas=total_entregas_list[i] if total_entregas_list else "1",
                        mod=mod_list[i] if mod_list else "",
                    )
                    cargas_salvas.append(carga_obj)

                # 🔹 ENTREGAS
                for i, numero in enumerate(entrega_numeros):
                    if not numero.strip():
                        continue

                    carga_index = int(entrega_carga_ref[i])
                    Entrega.objects.create(
                        numero=numero,
                        carga=cargas_salvas[carga_index]
                    )

        except ValueError:
            # erro controlado (carga duplicada)
            return render(request, self.template_name)

        except Exception as e:
            messages.error(request, f"Erro ao salvar: {e}")
            return render(request, self.template_name)

        messages.success(request, f"LECOM {lecom.lecom} criada com sucesso.")
        return render(request, self.template_name)

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
        data = self.request.GET.get("data")
        carga = self.request.GET.get("carga")
        veiculo = self.request.GET.get("veiculo")
        destino = self.request.GET.get("destino")
        
        if transporte_id and transporte_id.isdigit():
            queryset = queryset.filter(id=int(transporte_id))
            
        if lecom:
            queryset = queryset.filter(lecom__icontains=lecom)
        
        if status in ["LIBERADO", "BLOQUEADO"]:
            queryset = queryset.filter(status=status)
            
        if data:
            queryset = queryset.filter(data=data)
            
        if carga:
            queryset = queryset.filter(
                cargas__carga__icontains=carga
            ).distinct()
            
        if veiculo:
            queryset = queryset.filter(
                veiculo__tipo_veiculo=veiculo
            )
            
        if destino:
            queryset = queryset.filter(
                destino__icontains=destino
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 🔹 Select dinâmico de veículos
        context['veiculos'] = (
            Veiculo.objects
            .exclude(tipo_veiculo="Não informado")
            .values_list('tipo_veiculo', flat=True)
            .distinct()
            .order_by('tipo_veiculo')
        )

        # 🔹 Agrupamento de cargas por LECOM
        grupo_cargas = []
        for lecom in context["lecoms"]:
            grupo_cargas.append({
                "grupo": lecom,
                "cargas": lecom.cargas.all().order_by("seq")
            })

        context["grupo_cargas"] = grupo_cargas
        context["total_lecoms"] = context["lecoms"].count()

        # 🔹 Manter filtros no template
        context["filtro_transporte_id"] = self.request.GET.get("transporte_id", "")
        context["filtro_lecom"] = self.request.GET.get("lecom", "")
        context["filtro_status"] = self.request.GET.get("status", "")
        context["filtro_veiculo"] = self.request.GET.get("veiculo", "")
        context["filtro_carga"] = self.request.GET.get("carga", "")
        context["filtro_data"] = self.request.GET.get("data", "")

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

        # ==========================
        # Atualiza campos do Lecom
        # ==========================
        lecom.lecom = request.POST.get("lecom")
        lecom.destino = request.POST.get("destino")
        lecom.uf = request.POST.get("uf")
        lecom.data = request.POST.get("data")
        lecom.observacao = request.POST.get("observacao")
        lecom.status = request.POST.get("status", "BLOQUEADO")

        # Converte peso e m3 para Decimal
        try:
            lecom.peso = Decimal(request.POST.get("peso") or "0.00")
        except InvalidOperation:
            lecom.peso = Decimal("0.00")

        try:
            lecom.m3 = Decimal(request.POST.get("m3") or "0.00")
        except InvalidOperation:
            lecom.m3 = Decimal("0.00")

        lecom.save()

        # ==========================
        # Atualiza ou cria veículo
        # ==========================
        tipo_veiculo = request.POST.get("tipo_veiculo", "Não informado")
        if hasattr(lecom, 'veiculo'):
            lecom.veiculo.tipo_veiculo = tipo_veiculo
            lecom.veiculo.save()
        else:
            Veiculo.objects.create(lecom=lecom, tipo_veiculo=tipo_veiculo)

        # ==========================
        # Atualiza cargas do Lecom
        # ==========================
        carga_nomes = request.POST.getlist("carga[]")
        seqs = request.POST.getlist("seq[]")
        total_entregas_list = request.POST.getlist("total_entregas[]")
        mods = request.POST.getlist("mod[]")
        carga_ids = request.POST.getlist("carga_id[]")  # caso tenha hidden input com ID

        carga_queryset = list(lecom.cargas.all())

        for i, carga_nome in enumerate(carga_nomes):
            if carga_ids:
                carga = get_object_or_404(Carga, pk=carga_ids[i])
            elif i < len(carga_queryset):
                carga = carga_queryset[i]
            else:
                continue  # ignora se não tiver carga correspondente

            carga.carga = carga_nome
            carga.seq = int(seqs[i]) if seqs[i] else i + 1
            carga.total_entregas = total_entregas_list[i] if total_entregas_list[i] else "1"
            carga.mod = mods[i] if mods[i] else "-"
            carga.save()

        # ==========================
        # Cria/atualiza ControleSeparacao se Lecom liberada
        # ==========================
        if lecom.status == "LIBERADO":
            for carga in carga_queryset:
                controle, created = ControleSeparacao.objects.get_or_create(
                    lecom=lecom.lecom,
                    numero_transporte=carga.carga,
                    defaults={
                        "resumo": "1",
                        "destino": lecom.destino,
                        "uf": lecom.uf,
                        "peso": lecom.peso,
                        "m3": lecom.m3,
                        "data": lecom.data,
                        "observacao": lecom.observacao,
                        "tipo_veiculo": lecom.veiculo.tipo_veiculo if hasattr(lecom, "veiculo") else "Não informado",
                        "ot": "",
                        "outros_separadores": "",
                        "conferente": "",
                        "entregas": carga.total_entregas,
                        "mod": carga.mod,
                    }
                )

                # Atualiza campos editáveis se já existia
                if not created:
                    controle.entregas = carga.total_entregas
                    controle.mod = carga.mod
                    controle.save()

        return redirect(self.success_url)
    

    