from django.db import models


class CashRegister(models.Model):
    """
    Kassa — kirim/chiqim. Doktor davolashni yakunlaganda
    (Treatment narxi hisoblanganda) avtomatik 'kirim' yozuvi qo'shiladi.
    Admin qo'lda ham kirim/chiqim qo'shishi mumkin.
    """
    TYPE = [('income', 'Kirim'), ('expense', 'Chiqim')]
    transaction_type = models.CharField(max_length=10, choices=TYPE, verbose_name="Tur")
    amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Summa")
    description = models.CharField(max_length=300, verbose_name="Tavsif")
    patient = models.ForeignKey('patients.Patient', on_delete=models.SET_NULL, null=True, blank=True)
    treatment = models.ForeignKey('patients.Treatment', on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_transaction_type_display()} — {self.amount:,.0f} so'm"

    class Meta:
        verbose_name = "Kassa yozuvi"
        verbose_name_plural = "Kassa yozuvlari"
        ordering = ['-date']


class Expense(models.Model):
    CATEGORY = [
        ('salary', 'Maosh'), ('medicine', 'Dori-darmon'), ('equipment', 'Jihozlar'),
        ('utilities', 'Kommunal'), ('maintenance', "Ta'mirlash"), ('other', 'Boshqa'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY, verbose_name="Kategoriya")
    title = models.CharField(max_length=200, verbose_name="Nomi")
    amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Summa")
    date = models.DateField(verbose_name="Sana")
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.title} — {self.amount:,.0f} so'm"

    class Meta:
        verbose_name = "Xarajat"
        verbose_name_plural = "Xarajatlar"
        ordering = ['-date']
