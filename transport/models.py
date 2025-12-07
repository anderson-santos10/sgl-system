from django.db import models
from django.core.exceptions import ValidationError

class Transport(models.Model):
    lecom = models.CharField(max_length=10, default="")
    carga = models.CharField("Número da Carga", max_length=10)
    seq = models.PositiveIntegerField(blank=True, null=True)  # seq automática
    destino = models.CharField(max_length=150, default="")
    uf = models.CharField(max_length=2, default="")
    peso = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    m3 = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    data = models.DateField(verbose_name="Data da Carga")
    entregas = models.CharField(max_length=2, default="1")
    mod = models.CharField(max_length=10, default="")
    observacao = models.CharField(max_length=255, blank=True, default="")
    
    # Tipo de Veículo
    TIPO_VEICULO_CHOICES = [
        ("3/4", "3/4"),
        ("Toco", "Toco"),
        ("Carreta", "Carreta"),
        ("Truck", "Truck"),
        ("Rodotrem", "Rodotrem"),
        ("Container", "Container"),
        ("Utilitario", "Utilitário"),
    ]
    tipo_veiculo = models.CharField(max_length=20, choices=TIPO_VEICULO_CHOICES, blank=True, default="Não informado")
    
    STATUS_CHOICES = [
        ("Bloqueado", "Bloqueado"),
        ("Liberado", "Liberado"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Bloqueado")

    def save(self, *args, **kwargs):
        # Se seq não foi definido, calcula a próxima sequência do mesmo LECOM
        if self.seq is None:
            last_seq = Transport.objects.filter(lecom=self.lecom).order_by('-seq').first()
            self.seq = last_seq.seq + 1 if last_seq else 1

        # Validação para evitar seq duplicada
        if Transport.objects.filter(lecom=self.lecom, seq=self.seq).exclude(pk=self.pk).exists():
            raise ValidationError(f"Seq {self.seq} já existe para o LECOM {self.lecom}")

        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('lecom', 'seq')  # Garante unicidade no banco

    def __str__(self):
        return f"Carga {self.carga} (LECOM {self.lecom} - Seq {self.seq})"

class LecomGroup(models.Model):
    lecom = models.CharField(max_length=10, unique=True)
    veiculo = models.CharField(max_length=100, blank=True, default="")
    observacao = models.CharField(max_length=255, blank=True, default="")
    data = models.DateField(verbose_name="Data da Carga")

    def __str__(self):
        return f"LECOM {self.lecom}"
