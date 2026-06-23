import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinic_project.settings')
django.setup()

from accounts.models import User, Staff
from doctors.models import Specialization, Doctor, DoctorAvailability
from rooms.models import Ward, Cabinet
from pharmacy.models import MedicineCategory, Medicine
from datetime import date, time, timedelta

# Admin
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@klinika.uz', 'admin12345', role='admin')
    print("Admin yaratildi: admin / admin12345")
else:
    admin = User.objects.get(username='admin')
    admin.role = 'admin'
    admin.save()
    print("Admin allaqachon mavjud")

if not Staff.objects.filter(position='admin').exists():
    Staff.objects.create(first_name='Bosh', last_name='Administrator', position='admin', monthly_salary=10000000, hire_date=date.today())
    print("Admin xodim yozuvi qo'shildi")

# Specializations
specs = ['Kardiolog', 'Nevrolog', 'Pediatr', 'Jarroh', 'Stomatolog', 'Ginekolog', 'Oftalmolog', 'Dermatolog', 'LOR', 'Travmatolog', 'Endokrinolog', 'Urolog']
for s in specs:
    Specialization.objects.get_or_create(name=s)
print(f"{len(specs)} mutaxassislik qo'shildi")

# Cabinets (separate from wards!)
for num, floor in [('101', 1), ('102', 1), ('201', 2)]:
    Cabinet.objects.get_or_create(number=num, defaults={'floor': floor})
print("3 ta kabinet qo'shildi")

# Wards (separate from cabinets!)
if Ward.objects.count() == 0:
    Ward.objects.create(name='Umumiy palata 1', number='W101', ward_type='general', floor=1, total_beds=4, price_per_day=150000)
    Ward.objects.create(name='VIP palata', number='W201', ward_type='vip', floor=2, total_beds=1, price_per_day=500000)
    Ward.objects.create(name='Reanimatsiya', number='W301', ward_type='icu', floor=3, total_beds=2, price_per_day=800000)
    print("3 ta palata qo'shildi")

# Medicine categories
for c in ['Antibiotiklar', "Og'riq qoldiruvchi", 'Vitaminlar', 'Yurak dorilari', 'Allergiyaga qarshi']:
    MedicineCategory.objects.get_or_create(name=c)
print("Dori kategoriyalari qo'shildi")

# Medicines (admin sets price)
if Medicine.objects.count() == 0:
    antib = MedicineCategory.objects.get(name='Antibiotiklar')
    pain = MedicineCategory.objects.get(name="Og'riq qoldiruvchi")
    vit = MedicineCategory.objects.get(name='Vitaminlar')
    Medicine.objects.create(name='Amoksitsillin 500mg', category=antib, unit='pack', sell_price=25000, stock_quantity=100, min_stock=20)
    Medicine.objects.create(name='Paratsetamol', category=pain, unit='piece', sell_price=3000, stock_quantity=200, min_stock=30)
    Medicine.objects.create(name='Vitamin C', category=vit, unit='pack', sell_price=15000, stock_quantity=80, min_stock=15)
    Medicine.objects.create(name='Ibuprofen', category=pain, unit='pack', sell_price=18000, stock_quantity=60, min_stock=15)
    print("4 ta mahsulot qo'shildi")

# Sample doctor with availability
if Doctor.objects.filter(user__username='aziz.karimov').exists():
    print("Namuna shifokor allaqachon mavjud")
else:
    kardiolog = Specialization.objects.get(name='Kardiolog')
    cab101 = Cabinet.objects.get(number='101')
    user = User.objects.create_user(username='aziz.karimov', password='doctor123', first_name='Aziz', last_name='Karimov', phone='+998901234567', role='doctor')
    today = date.today()
    doctor = Doctor.objects.create(
        user=user, first_name='Aziz', last_name='Karimov', phone='+998901234567',
        gender='M', specialization=kardiolog, experience_years=15,
        consultation_price=150000, cabinet=cab101, bio='Yurak kasalliklari bo\'yicha 15 yillik tajriba.'
    )
    Staff.objects.create(first_name='Aziz', last_name='Karimov', position='doctor', phone='+998901234567', doctor=doctor, monthly_salary=8000000, hire_date=today)
    # Add some availability slots
    for i in range(1, 6):
        d = today + timedelta(days=i)
        for hour in [9, 10, 11, 14, 15]:
            DoctorAvailability.objects.create(
                doctor=doctor, date=d, start_time=time(hour, 0), end_time=time(hour, 30)
            )
    print("1 ta namuna shifokor (login: aziz.karimov / parol: doctor123) + bo'sh vaqtlar qo'shildi")

# Sample nurse and cleaner (no login needed)
if not Staff.objects.filter(position='nurse').exists():
    Staff.objects.create(first_name='Nilufar', last_name='Eshmatova', position='nurse', phone='+998933334455', monthly_salary=4500000, hire_date=date.today())
    print("1 ta namuna hamshira qo'shildi")
if not Staff.objects.filter(position='cleaner').exists():
    Staff.objects.create(first_name='Botir', last_name='Rahimov', position='cleaner', phone='+998944445566', monthly_salary=3000000, hire_date=date.today())
    print("1 ta namuna farrosh qo'shildi")

print("\n=== Seed data tayyor! ===")
print("Admin: admin / admin12345")
print("Doktor: aziz.karimov / doctor123")
