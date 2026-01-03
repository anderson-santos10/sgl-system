from django.db import models
from django.utils import timezone

class NotaFiscal(models.Model):
    TURNO_CHOICES = [
        (1, "Turno 1"),
        (2, "Turno 2"),
        (3, "Turno 3"),
    ]

    data = models.DateField(default=timezone.now, verbose_name="Data")
    turno = models.IntegerField(choices=TURNO_CHOICES, verbose_name="Turno")
    nf = models.CharField(max_length=10, unique=True, verbose_name="Número da Nota")
    un_origem = models.CharField(max_length=4, verbose_name="UN Origem")
    qnt_pallet = models.PositiveSmallIntegerField(verbose_name="Quantidade de Pallets")
    tipo_veiculo = models.CharField(max_length=50, verbose_name="Tipo de Veículo")
    peso_nota = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Peso da Nota (kg)")

    def __str__(self):
        return (
            f"Nota {self.nf} - "
            f"Turno {self.get_turno_display()} - "
            f"{self.data} - "
            f"UN Origem {self.un_origem} - "
            f"QNT {self.qnt_pallet} - "
            f"Veículo {self.tipo_veiculo} - "
            f"Peso {self.peso_nota} kg"
        )



