from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView
from django.contrib import messages
from decimal import Decimal, InvalidOperation
from django.db import transaction
from django.utils.dateparse import parse_date
from .models import Lecom, Carga, Entrega, Veiculo
from expedicao.services import sincronizar_expedicao


# Função auxiliar para Decimal
def safe_decimal(value, default=Decimal("0.00")):
    if value is None:
        return default
    try:
        value = str(value).replace(",", ".").strip()
        return Decimal(value)
    except (InvalidOperation, ValueError):
        return default

# Criar Transporte
class CriarTransporteView(View):
    template_name = "transport/inserir_carga.html"

    def get(self, request):
        return render(
            request,
            self.template_name,
            {
                "status_default": "BLOQUEADO"
            }
        )

    def post(self, request):
        lecom_code = request.POST.get("lecom", "").strip()
        destino = request.POST.get("destino", "").strip()
        uf = request.POST.get("uf", "").strip()
        peso = safe_decimal(request.POST.get("peso"))
        m3 = safe_decimal(request.POST.get("m3"))
        data = parse_date(request.POST.get("data", "").strip())
        observacao = request.POST.get("observacao", "").strip()
        status = request.POST.get("status", "BLOQUEADO")

        errors = []
        if not lecom_code:
            errors.append("O campo LECOM é obrigatório.")
        if not destino:
            errors.append("O campo Destino é obrigatório.")
        if not uf:
            errors.append("O campo UF é obrigatório.")
        if not data:
            errors.append("Data inválida.")

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, self.template_name)

        if Lecom.objects.filter(lecom=lecom_code).exists():
            messages.error(request, "Já existe um transporte com esse número de LECOM.")
            return render(request, self.template_name)

        tipo_veiculo = request.POST.get("tipo_veiculo", "Não informado")
        cargas_list = request.POST.getlist("carga[]")
        seq_list = request.POST.getlist("seq[]")
        total_entregas_list = request.POST.getlist("total_entregas[]")
        mod_list = request.POST.getlist("mod[]")
        entrega_numeros = request.POST.getlist("entrega_numero[]")
        entrega_carga_ref = request.POST.getlist("entrega_carga_index[]")

        if not cargas_list:
            messages.error(request, "Informe ao menos uma carga.")
            return render(request, self.template_name)

        try:
            with transaction.atomic():
                # LECOM
                lecom = Lecom.objects.create(
                    lecom=lecom_code,
                    destino=destino,
                    uf=uf,
                    peso=peso,
                    m3=m3,
                    data=data,
                    observacao=observacao,
                    status=status,
                )

                # Veículo
                Veiculo.objects.create(
                    lecom=lecom,
                    tipo_veiculo=tipo_veiculo
                )

                # Cargas
                cargas_salvas = []
                for i, carga_num in enumerate(cargas_list):
                    if Carga.objects.filter(lecom=lecom, carga=carga_num).exists():
                        messages.error(
                            request,
                            f"A carga {carga_num} já existe para este LECOM."
                        )
                        raise ValueError

                    carga_obj = Carga.objects.create(
                        lecom=lecom,
                        carga=carga_num,
                        seq=int(seq_list[i]) if seq_list and seq_list[i] else i + 1,
                        total_entregas=total_entregas_list[i] if total_entregas_list and total_entregas_list[i] else "1",
                        mod=mod_list[i] if mod_list and mod_list[i] else "-",
                    )
                    cargas_salvas.append(carga_obj)

                # Entregas
                for i, numero in enumerate(entrega_numeros):
                    if not numero.strip():
                        continue
                    carga_index = int(entrega_carga_ref[i])
                    Entrega.objects.create(
                        numero=numero,
                        carga=cargas_salvas[carga_index]
                    )

                # 🔄 Sincroniza com expedição
                sincronizar_expedicao(lecom)

        except ValueError:
            return render(request, self.template_name)

        except Exception:
            messages.error(request, "Erro inesperado ao salvar o transporte.")
            return render(request, self.template_name)

        messages.success(request, f"LECOM {lecom.lecom} criado com sucesso.")
        return render(request, self.template_name)


class CenarioTransporteView(ListView):
    model = Lecom
    template_name = "transport/cenario_transporte.html"
    context_object_name = "lecoms"
    ordering = ["-id"]

    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related("cargas", "veiculo")

        # Filtragem via GET
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
            queryset = queryset.filter(cargas__carga__icontains=carga).distinct()
        if veiculo:
            queryset = queryset.filter(veiculo__tipo_veiculo=veiculo)
        if destino:
            queryset = queryset.filter(destino__icontains=destino)

        # Garante que peso e m3 sejam Decimal válidos
        for lecom_obj in queryset:
            lecom_obj.peso = safe_decimal(lecom_obj.peso)
            lecom_obj.m3 = safe_decimal(lecom_obj.m3)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Veículos para o filtro 
        context["veiculos"] = Veiculo.TIPO_VEICULO_CHOICES

        # Agrupamento de cargas por lecom
        grupo_cargas = []
        for lecom_obj in context["lecoms"]:
            grupo_cargas.append({
                "grupo": lecom_obj,
                "cargas": lecom_obj.cargas.all().order_by("seq")
            })
        context["grupo_cargas"] = grupo_cargas
        context["total_lecoms"] = context["lecoms"].count()

        return context


class EditarTransporteView(View):
    template_name = "transport/inserir_carga.html"
    success_url = reverse_lazy("transport:cenario_transporte")

    def get(self, request, pk):
        lecom = get_object_or_404(Lecom, pk=pk)
        cargas = lecom.cargas.all().order_by("seq")
        return render(request, self.template_name, {
            "lecom": lecom,
            "cargas": cargas,
            "modo_edicao": True
        })

    def post(self, request, pk):
        lecom = get_object_or_404(Lecom, pk=pk)

        try:
            # Atualiza campos do Lecom
            lecom.lecom = request.POST.get("lecom")
            lecom.destino = request.POST.get("destino")
            lecom.uf = request.POST.get("uf")
            lecom.data = request.POST.get("data")
            lecom.observacao = request.POST.get("observacao")
            lecom.status = request.POST.get("status", "BLOQUEADO")
            lecom.peso = safe_decimal(request.POST.get("peso"))
            lecom.m3 = safe_decimal(request.POST.get("m3"))
            lecom.save()

            # Atualiza veículo
            tipo_veiculo = request.POST.get("tipo_veiculo", "Não informado")
            Veiculo.objects.update_or_create(
                lecom=lecom,
                defaults={"tipo_veiculo": tipo_veiculo}
            )

            # Atualiza cargas
            carga_nomes = request.POST.getlist("carga[]")
            seqs = request.POST.getlist("seq[]")
            total_entregas_list = request.POST.getlist("total_entregas[]")
            mods = request.POST.getlist("mod[]")
            carga_ids = request.POST.getlist("carga_id[]")
            cargas_existentes = list(lecom.cargas.all().order_by("seq"))

            for i, carga_nome in enumerate(carga_nomes):
                if carga_ids and i < len(carga_ids):
                    carga = get_object_or_404(Carga, pk=carga_ids[i])
                elif i < len(cargas_existentes):
                    carga = cargas_existentes[i]
                else:
                    continue

                carga.carga = carga_nome
                carga.seq = int(seqs[i]) if i < len(seqs) and seqs[i] else i + 1
                carga.total_entregas = (
                    total_entregas_list[i]
                    if i < len(total_entregas_list) and total_entregas_list[i]
                    else "1"
                )
                carga.mod = mods[i] if i < len(mods) and mods[i] else "-"
                carga.save()

            # 🔄 Regras de negócio da expedição
            sincronizar_expedicao(lecom)

            messages.success(request, "Transporte atualizado com sucesso.")
            return redirect(self.success_url)

        except Exception:
            messages.error(request, "Erro ao atualizar o transporte.")

            cargas = lecom.cargas.all().order_by("seq")

            return render(request, self.template_name, {
                "lecom": lecom,
                "cargas": cargas,
                "modo_edicao": True
            })



