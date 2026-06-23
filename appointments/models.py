from django.db import models


class Appointment(models.Model):
    """
    Bemor doktorni va bo'sh vaqtni tanlab band qiladi.
    Agar tanlangan vaqt band bo'lsa -> "Vaqt yo'q" chiqadi (view darajasida tekshiriladi).
    """
    STATUS = [
        ('booked', 'Band qilingan'),
        ('completed', 'Yakunlangan'),
        ('cancelled', 'Bekor qilingan'),
    ]
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey('doctors.Doctor', on_delete=models.CASCADE, related_name='appointments')
    availability = models.OneToOneField('doctors.DoctorAvailability', on_delete=models.CASCADE, related_name='appointment')
    complaint = models.TextField(blank=True, verbose_name="Shikoyat / sabab")
    status = models.CharField(max_length=20, choices=STATUS, default='booked')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient} -> {self.doctor} ({self.availability.date} {self.availability.start_time})"

    class Meta:
        verbose_name = "Navbat (qabul)"
        verbose_name_plural = "Navbatlar (qabullar)"
        ordering = ['-created_at']
