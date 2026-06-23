from django.db import models


class Operation(models.Model):
    STATUS = [
        ('scheduled', 'Rejalashtirilgan'),
        ('completed', 'Yakunlangan'),
        ('cancelled', 'Bekor qilingan'),
    ]
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='operations')
    lead_surgeon = models.ForeignKey('doctors.Doctor', on_delete=models.SET_NULL, null=True, related_name='operations')
    operation_name = models.CharField(max_length=300, verbose_name="Operatsiya nomi")
    operation_room = models.CharField(max_length=50, verbose_name="Operatsiya xonasi")
    scheduled_date = models.DateTimeField(verbose_name="Vaqti")
    price = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="Narxi")
    status = models.CharField(max_length=20, choices=STATUS, default='scheduled')
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.operation_name} — {self.patient}"

    class Meta:
        verbose_name = "Operatsiya"
        verbose_name_plural = "Operatsiyalar"
        ordering = ['-scheduled_date']
