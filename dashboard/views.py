from django.views.generic import TemplateView
from django.utils import timezone
from receipt.models import NotaFiscal
from django.db.models import Sum

class CardView(TemplateView):
    template_name = "dashboard/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hoje = timezone.localdate()
        context['hoje'] = hoje.strftime("%d/%m/%Y")

        # Queryset base
        notas_qs = NotaFiscal.objects.all()
        notas_hj_qs = notas_qs.filter(data=hoje)

        # -------------------- NFs --------------------
        context['notas'] = notas_qs.count()  # total NFs
        context['nf_total_hj'] = notas_hj_qs.count()  # total NFs hoje

        # NFs de hoje por UN
        context['nf_total_hj_un10'] = notas_hj_qs.filter(un_origem__iexact="un10").count()
        context['nf_total_hj_un20'] = notas_hj_qs.filter(un_origem__iexact="un20").count()
        context['nf_total_hj_un40'] = notas_hj_qs.filter(un_origem__iexact="un40").count()

        # Total de NFs por UN (independente da data)
        context['un10'] = notas_qs.filter(un_origem__iexact="un10").count()
        context['un20'] = notas_qs.filter(un_origem__iexact="un20").count()
        context['un40'] = notas_qs.filter(un_origem__iexact="un40").count()

        # -------------------- Pallets --------------------
        context['total_pallets'] = notas_qs.aggregate(total=Sum('qnt_pallet'))['total'] or 0
        context['total_pallets_hj'] = notas_hj_qs.aggregate(total=Sum('qnt_pallet'))['total'] or 0
        context['total_pallets_hj_un10'] = notas_hj_qs.filter(un_origem__iexact="un10").aggregate(total=Sum('qnt_pallet'))['total'] or 0
        context['total_pallets_hj_un20'] = notas_hj_qs.filter(un_origem__iexact="un20").aggregate(total=Sum('qnt_pallet'))['total'] or 0
        context['total_pallets_hj_un40'] = notas_hj_qs.filter(un_origem__iexact="un40").aggregate(total=Sum('qnt_pallet'))['total'] or 0

        # -------------------- Peso bruto --------------------
        context['total_peso'] = notas_qs.aggregate(total=Sum('peso_nota'))['total'] or 0
        context['total_peso_hj'] = notas_hj_qs.aggregate(total=Sum('peso_nota'))['total'] or 0
        context['total_peso_hj_un10'] = notas_hj_qs.filter(un_origem__iexact="un10").aggregate(total=Sum('peso_nota'))['total'] or 0
        context['total_peso_hj_un20'] = notas_hj_qs.filter(un_origem__iexact="un20").aggregate(total=Sum('peso_nota'))['total'] or 0
        context['total_peso_hj_un40'] = notas_hj_qs.filter(un_origem__iexact="un40").aggregate(total=Sum('peso_nota'))['total'] or 0

        return context
