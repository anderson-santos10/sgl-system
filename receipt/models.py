from django.db import models
from django.utils import timezone
# Create your models here.


class NotaFiscal(models.Model):
    TURNO_CHOICES = [
        (1, "Turno 1"),
        (2, "Turno 2"),
        (3, "Turno 3"),
    ]
    

    data = models.DateField(default=timezone.now)
    turno = models.IntegerField(choices=TURNO_CHOICES)
    nf = models.CharField(max_length=10, unique=True, verbose_name="Número da Nota")
    un_origem = models.CharField(max_length=4)
    qnt_pallet = models.CharField(max_length=2)
    tipo_veiculo = models.CharField(max_length=50)
    peso_nota = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Nota {self.nf} - Turno {self.turno} - {self.data} - UN Origem {self.un_origem} - QNT {self.turno} - Veiculo {self.turno} - Peso {self.turno}"



