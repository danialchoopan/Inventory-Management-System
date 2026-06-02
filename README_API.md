# Inventory Management API 🚀

This document details the available API endpoints and authentication flow for the Inventory Management System.

## Base URL
`/inventory` (Inventory operations)
`/auth` (Authentication)

## Authentication 🔐

The API uses JWT-based authentication.

### Login
- **URL**: `/auth/login`
- **Method**: `POST`
- **Data**: `username`, `password` (Form data)
- **Response**: `{ "access_token": "...", "token_type": "bearer" }`

Include the token in the header of subsequent requests:
`Authorization: Bearer <your_token>`

## Role-Based Access Control (RBAC) 🛡️

| Role | Description | Permissions |
| :--- | :--- | :--- |
| **MANAGER** | System Admin | Full access (CRUD Products, All Transactions) |
| **SELLER** | Sales Staff | Read Products, Sales & Returns only |
| **WORKER** | Warehouse Staff | Read Products, Stock Adjustments (Counting) only |

## Endpoints Summary

### User Profile
- `GET /inventory/me`: Returns current user info.

### Products
- `GET /inventory/products`: List all products (All roles).
- `POST /inventory/products`: Create new product (**MANAGER** only).
- `GET /inventory/products/{sku}`: Get product details (All roles).
- `PUT /inventory/products/{sku}`: Update product details (**MANAGER** only).

### Stock Operations
- `POST /inventory/products/{sku}/stock`: Update stock level.
  - Workers can only use `ADJUSTMENT`.
  - Sellers can use `SALE` or `RETURN`.
  - Managers can use any type.

### History & Auditing
- `GET /inventory/products/{id}/transactions`: List transactions for a product.
- `GET /inventory/products/{id}/history`: List price/stock history for a product.

---

*Note: All product names and descriptions support Persian (UTF-8) characters.*
