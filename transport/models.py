from django.db import models
from decimal import Decimal
from django.db import models


class Lecom(models.Model):

    STATUS_CHOICES = [
        ('LIBERADO', 'Liberado'),
        ('BLOQUEADO', 'Bloqueado'),
    ]

    lecom = models.CharField(max_length=10)
    destino = models.CharField(max_length=150)
    uf = models.CharField(max_length=2)

    peso = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("0.00")
    )

    m3 = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("0.00")
    )

    data = models.DateField(verbose_name="Data da Carga")
    observacao = models.CharField(max_length=255, blank=True)

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='BLOQUEADO'
    )

    def __str__(self):
        return f'{self.lecom} - {self.get_status_display()}'



class Carga(models.Model):
    lecom = models.ForeignKey(Lecom, on_delete=models.CASCADE, related_name="cargas")
    carga = models.CharField("Número da Carga", max_length=10)
    seq = models.PositiveIntegerField(blank=True, null=True)
    total_entregas = models.CharField(max_length=2, default="1")
    mod = models.CharField(max_length=10, default="-")


class Entrega(models.Model):
    numero = models.CharField(max_length=10)
    carga = models.ForeignKey(Carga, on_delete=models.CASCADE, related_name="entregas")


class Mod(models.Model):
    codigo = models.CharField(max_length=10)
    carga = models.ForeignKey(Carga, on_delete=models.CASCADE, related_name="mods")


class Veiculo(models.Model):
    TIPO_VEICULO_CHOICES = [
        ("3/4", "3/4"),
        ("Toco", "Toco"),
        ("Carreta", "Carreta"),
        ("Truck", "Truck"),
        ("Rodotrem", "Rodotrem"),
        ("Container", "Container"),
        ("Utilitario", "Utilitário"),
    ]
    tipo_veiculo = models.CharField(
        max_length=20, choices=TIPO_VEICULO_CHOICES, blank=True, default="Não informado")
    lecom = models.OneToOneField(
        Lecom, on_delete=models.CASCADE, related_name="veiculo")
