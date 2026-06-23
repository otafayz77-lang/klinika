from django.db import models


class MedicineCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="Kategoriya nomi")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Dori kategoriyasi"
        verbose_name_plural = "Dori kategoriyalari"


class Medicine(models.Model):
    """
    Mahsulot/dori. Narx va miqdorni FAQAT ADMIN kiritadi/o'zgartiradi.
    Doktor davolashda shu ro'yxatdan tanlaydi, narxni o'zi kiritmaydi.
    """
    UNIT = [('piece', 'Dona'), ('pack', 'Paket'), ('bottle', 'Shisha'), ('box', 'Quti'), ('ml', 'ml'), ('g', 'gramm')]
    name = models.CharField(max_length=200, verbose_name="Nomi")
    category = models.ForeignKey(MedicineCategory, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Kategoriya")
    unit = models.CharField(max_length=10, choices=UNIT, default='piece', verbose_name="O'lchov birligi")
    sell_price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Sotish narxi (so'm)")
    stock_quantity = models.PositiveIntegerField(default=0, verbose_name="Zaxiradagi miqdor")
    min_stock = models.PositiveIntegerField(default=10, verbose_name="Minimal zaxira")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.sell_price:,.0f} so'm)"

    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.min_stock

    class Meta:
        verbose_name = "Dori / Mahsulot"
        verbose_name_plural = "Dorilar / Mahsulotlar"
        ordering = ['name']


class MedicineIncome(models.Model):
    """Admin tomonidan dori kelishi qayd etiladi — zaxirani oshiradi."""
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='incomes')
    quantity = models.PositiveIntegerField(verbose_name="Miqdor")
    purchase_price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Kelish narxi (dona uchun)")
    supplier = models.CharField(max_length=200, blank=True, verbose_name="Yetkazuvchi")
    date = models.DateField(verbose_name="Sana")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.medicine.stock_quantity = self.medicine.stock_quantity + int(self.quantity)
            self.medicine.save(update_fields=['stock_quantity'])
            # Kassa yozuvi endi viewda qo'shiladi (yanada ishonchli)

    def __str__(self):
        return f"{self.medicine} +{self.quantity}"

    class Meta:
        verbose_name = "Dori kelishi"
        verbose_name_plural = "Dori kelishlari"
        ordering = ['-date']
