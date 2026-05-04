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
