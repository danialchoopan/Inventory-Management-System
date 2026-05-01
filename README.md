# Inventory Management System 📦

A modern, scalable, and high-performance inventory management system built with **FastAPI**, **PostgreSQL**, and **Redis**. This project is designed following **Clean Architecture** principles to ensure readable, testable, and maintainable code.


## ✨ Key Features

### 1. Optimistic Locking for Concurrency Control 🔒
One of the biggest challenges in inventory systems is race conditions (e.g., two users buying the last item simultaneously).
- We use a `version` column in the `products` table.
- When updating stock, if the `version` in the database differs from the one in memory, the transaction is rejected.
- This prevents **Race Conditions** and ensures data integrity without heavy database locking.

### 2. Clean Architecture 🏗️
The code is separated into distinct layers:
- **Presentation Layer**: FastAPI routers and Pydantic models.
- **Service Layer**: Business logic, stock calculations, and error handling.
- **Repository Layer**: Direct database interactions (SQLAlchemy).
- **Infrastructure**: Database connections, Redis, and configurations.

### 3. Smart Caching with Redis ⚡
- Product details are cached in **Redis** (TTL: 5 minutes).
- This significantly reduces load on PostgreSQL and speeds up API responses.
- Cache is invalidated automatically whenever a product is updated to prevent stale data.

### 4. Comprehensive Auditing & History 📊
- Every stock change (Purchase, Sale, Return) is recorded in `inventory_transactions`.
- Price and stock snapshots are saved in `stock_history` for trend analysis and auditing purposes.

### 5. Rate Limiting 🛡️
- To prevent abuse or DDoS attacks, sensitive endpoints (like stock updates) are rate-limited based on IP address using Redis.

---

## 🛠️ Tech Stack

- **Language**: Python 3.10+
- **Web Framework**: FastAPI (Async)
- **Database**: PostgreSQL (with SQLAlchemy Async)
- **Cache**: Redis
- **Validation**: Pydantic V2
- **Package Manager**: Pip

---

## 📂 Project Structure

```text
app/
├── api/                # Presentation Layer (Router & Schemas)
│   ├── routes.py       # API Endpoint definitions
│   └── schemas.py      # Pydantic Input/Output models
├── core/               # Core Configuration
│   └── config.py       # Environment variables & settings
├── models/             # Database Models (SQLAlchemy)
│   └── inventory.py    # Tables: Products, Transactions, History
├── repositories/       # Data Access Layer
│   └── inventory_repo.py # Database queries
├── services/           # Business Logic Layer
│   └── inventory_service.py # Transaction management, Caching, Locking
├── infrastructure/     # Infrastructure Setup
│   └── database.py     # DB & Redis connections
└── main.py             # Application Entry Point

# سیستم مدیریت موجودی انبار  📦

یک سیستم مدیریت موجودی مدرن، مقیاس‌پذیر و با کارایی بالا که با استفاده از **FastAPI**، **PostgreSQL** و **Redis** ساخته شده است. این پروژه بر اساس اصول **معماری تمیز (Clean Architecture)** طراحی شده تا کدی خوانا، قابل تست و قابل نگهداری ارائه دهد.


## ✨ ویژگی‌های کلیدی

### 1. کنترل همزمانی با قفل‌گذاری خوش‌بینانه (Optimistic Locking) 🔒
یکی از چالش‌های بزرگ در سیستم‌های انبارداری، تداخل درخواست‌هاست (مثاً دو نفر همزمان آخرین کالا را بخرند).
- ما از ستون `version` در جدول محصولات استفاده می‌کنیم.
- هنگام آپدیت موجودی، اگر نسخه (`version`) رکورد در دیتابیس با نسخه‌ای که در حافظه داریم متفاوت باشد، تراکنش رد می‌شود.
- این روش از **Race Condition** جلوگیری کرده و یکپارچگی داده‌ها را تضمین می‌کند.

### 2. معماری تمیز (Clean Architecture) 🏗️
کد به لایه‌های مجزا تقسیم شده است:
- **Presentation Layer**: روترهای FastAPI و مدل‌های Pydantic.
- **Service Layer**: منطق کسب‌وکار، محاسبات موجودی و مدیریت خطاها.
- **Repository Layer**: تعامل مستقیم با دیتابیس (SQLAlchemy).
- **Infrastructure**: تنظیمات دیتابیس، Redis و کانفیگ‌ها.

### 3. کشینگ هوشمند با Redis ⚡
- اطلاعات محصولات در **Redis** کش می‌شوند (TTL: ۵ دقیقه).
- این کار تعداد کوئری‌های سنگین به PostgreSQL را کاهش داده و سرعت پاسخ‌دهی API را به شدت افزایش می‌دهد.
- با هر تغییر در محصول، کش مربوطه باطل (Invalidated) می‌شود تا داده‌های قدیمی نمایش داده نشوند.


### 4. تاریخچه کامل و حسابرسی (Auditing) 📊
- هر تغییری در موجودی (خرید، فروش، مرجوعی) در جدول `inventory_transactions` ثبت می‌شود.
- تغییرات قیمت و موجودی در جدول `stock_history` ذخیره می‌شوند تا امکان تحلیل روند و حسابرسی فراهم باشد.

### 5. محدودیت نرخ درخواست (Rate Limiting) 🛡️
- برای جلوگیری از حملات DDOS یا استفاده نادرست، اندپوینت‌های حساس (مثل آپدیت موجودی) دارای محدودیت تعداد درخواست بر اساس IP هستند.

---

## 🛠️ تکنولوژی‌های استفاده شده

- **زبان برنامه‌نویسی**: Python 3.10+
- **فریم‌ورک وب**: FastAPI (Async)
- **دیتابیس**: PostgreSQL (با SQLAlchemy Async)
- **کش**: Redis
- **اعتبارسنجی داده**: Pydantic V2
- **مدیریت پکیج**: Pip

---

## 📂 ساختار پروژه

```text
app/
├── api/                # لایه ارائه (Router & Schemas)
│   ├── routes.py       # تعریف اندپوینت‌های API
│   └── schemas.py      # مدل‌های ورودی و خروجی Pydantic
├── core/               # تنظیمات اصلی
│   └── config.py       # متغیرهای محیطی و کانفیگ
├── models/             # مدل‌های دیتابیس (SQLAlchemy)
│   └── inventory.py    # تعریف جداول Products, Transactions, History
├── repositories/       # لایه دسترسی به داده
│   └── inventory_repo.py # کوئری‌های دیتابیس
├── services/           # لایه منطق کسب‌وکار
│   └── inventory_service.py # مدیریت تراکنش‌ها، کش و قفل‌گذاری
├── infrastructure/     # زیرساخت
│   └── database.py     # اتصال به DB و Redis
└── main.py             # نقطه ورود برنامه