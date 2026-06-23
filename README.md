# KlinikaPro v2 — Rolga asoslangan klinika boshqaruv tizimi

Bu tizimda 3 xil rol mavjud: **Admin**, **Shifokor**, **Bemor** — har biri o'z sahifasiga ega.

## Qanday ishlaydi

### Admin
- Shifokor qo'shadi → tizim avtomatik **login va parol** yaratadi (ekranda bir marta ko'rsatiladi)
- Mahsulot/dori narxi va miqdorini kiritadi
- Palata (yotish bo'limi) va Kabinet (qabul xonasi) — **butunlay alohida** bo'limlar
- Kassa, xarajatlar, operatsiyalarni boshqaradi
- Bemorlar ro'yxatida **faqat navbat olgan** (band qilgan) bemorlar ko'rinadi

### Shifokor
- Admin bergan login/parol bilan kiradi
- **O'z bo'sh vaqtlarini o'zi kiritadi** (sana + boshlanish/tugash vaqti)
- O'ziga navbat olgan bemorlarni ko'radi
- **Faqat konsultatsiya narxini o'zi tahrirlaydi** — boshqa shaxsiy ma'lumotlarini faqat admin o'zgartiradi
- **O'z ko'rik xizmatlarini yaratadi** (masalan EKG, USG) — davolashda konsultatsiyaga qo'shimcha tanlanadi
- Bemorni davolashda **dori/mahsulot va qo'shimcha xizmat tanlaydi -> narx avtomatik hisoblanadi** va kassaga avtomatik kirim qo'shiladi
- Mahsulot zaxirasi avtomatik kamayadi

### Bemor
- **O'zi onlayn ro'yxatdan o'tadi** (login yaratadi) — `/register/` orqali
- Ro'yxatdan o'tgani "bemor qo'shildi" degani emas — faqat **birinchi marta navbat olgandan keyin** admin ro'yxatida ko'rinadi
- Shifokor tanlab, uning bo'sh vaqtlaridan birini tanlab navbat band qiladi
- Agar vaqt band bo'lsa -> **"Vaqt yo'q"** xabari chiqadi, boshqa vaqt tanlashi kerak
- O'z davolanish tarixini (tashxis, ishlatilgan dorilar, narxlar) ko'radi

### Hodimlar (Admin -> Sozlamalar -> Hodimlar)
- Admin, Shifokor, Hamshira, Farrosh va boshqa xodimlar bitta ro'yxatda
- Shifokor qo'shilganda Hodimlar ro'yxatiga **avtomatik** qo'shiladi (lavozimi o'zgartirib bo'lmaydi, chunki Shifokor profilidan boshqariladi)
- Hamshira/farrosh kabi xodimlarning kirish huquqi yo'q — faqat ism, lavozim, telefon, oylik maosh saqlanadi
- **Oylik to'lash**: har bir xodim uchun belgilangan oylik maosh bor; admin "Oylikni to'lash" tugmasini bosganda shu summa **avtomatik Xarajatlarga** yoziladi va to'lov tarixi saqlanadi
- Bir oyda bir martadan ortiq to'lab bo'lmaydi (tizim oldini oladi)
- Agar xodim shifokor bo'lsa, uning login parolini ham shu yerdan tiklash mumkin

## O'rnatish

```bash
# 1. Virtual muhit
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 2. Paketlar
pip install -r requirements.txt

# 3. Bazani yaratish — MUHIM, albatta bajaring
python manage.py migrate

# 4. Boshlang'ich ma'lumotlar (admin, namuna shifokor, palatalar, dorilar)
python manage.py shell < seed_data.py

# 5. Serverni ishga tushirish
python manage.py runserver
```

Brauzerda: **http://127.0.0.1:8000/**

### Tayyor kirish ma'lumotlari (seed_data.py dan keyin)

| Rol | Login | Parol |
|---|---|---|
| Admin | `admin` | `admin12345` |
| Namuna shifokor | `aziz.karimov` | `doctor123` |

Bemor sifatida sinab ko'rish uchun **"Ro'yxatdan o'ting"** havolasidan o'zingiz ro'yxatdan o'ting.

Admin panel (Django): **http://127.0.0.1:8000/admin/**

## Asosiy oqim (test qilish uchun)

1. `admin` bilan kiring -> Shifokorlar -> Shifokor qo'shish -> yangi shifokor yarating, login/parolni saqlab qo'ying
2. Chiqib, yangi yaratilgan shifokor bilan kiring -> Bo'sh vaqtlarim -> bir nechta sana/vaqt qo'shing
3. Chiqib, Ro'yxatdan o'ting orqali bemor sifatida ro'yxatdan o'ting
4. Navbat olish -> shifokorni tanlang -> bo'sh vaqtni tanlang -> band qiling
5. Shifokor bilan qayta kiring -> Bosh sahifadagi bugungi qabulda bemorni ko'rasiz -> Davolash tugmasi orqali tashxis qo'yib, dori tanlang
6. Narx avtomatik hisoblanadi, kassaga tushadi
7. admin bilan kirib Kassa va Bemorlar bo'limlarida natijani ko'ring

## Loyiha tuzilishi

```
clinic_project/
├── accounts/        # User model (role: admin/doctor/patient), login/register
├── doctors/         # Shifokor profili, mutaxassislik, bo'sh vaqtlar
├── patients/        # Bemor profili, davolash yozuvlari (Treatment)
├── appointments/    # Navbat band qilish
├── rooms/           # Ward (palata/yotish) va Cabinet (qabul xonasi) — ALOHIDA
├── pharmacy/        # Dori/mahsulotlar, kelishi (faqat admin narx kiritadi)
├── finance/         # Kassa (avtomatik to'ladi), xarajatlar
├── operations/      # Operatsiyalar
└── templates/       # Har bir rol uchun alohida shablonlar
```

## Texnologiyalar

- Django 5.x, custom `User` modeli (`role` maydoni bilan)
- SQLite (production uchun PostgreSQL tavsiya etiladi)
- Sof HTML/CSS/JS — frontend frameworksiz
- Font: Fraunces (sarlavhalar) + Inter (matn)

## Production uchun

- `DEBUG = False`, `SECRET_KEY`ni environment variable orqali bering
- `ALLOWED_HOSTS` ni cheklang
- PostgreSQL'ga o'tkazing
- Gunicorn + Nginx orqali deploy qiling
