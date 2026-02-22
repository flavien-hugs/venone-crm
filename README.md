# PROPERTY MANAGEMENT APPLICATION

[![Flask Version](https://img.shields.io/badge/Flask-2.x-lightgrey.svg)](https://flask.palletsprojects.com/)
[![Python Version](https://img.shields.io/badge/Python-3.10-brightgreen.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Description

Venone CRM is a professional property management application designed for real estate agencies, landlords,
and administrators. It facilitates rental management, payment tracking, and automated alerts via SMS and email.

## Key Features

- **Real Estate Management**: Specialized interfaces for agencies and landlords.
- **Rental Tracking**: Management of rental units, tenant assignments, and contracts.
- **Payment System**: Recording deposits, advances, and rental payments.
- **Automated Fees**: Automatic deduction of management fees on the 10th of each month.
- **Penalty System**: Automatic 10% penalty for payments made after the 15th.
- **Smart Alerts**: SMS and software alerts for payment arrears and eviction notices (after 3 months).
- **Communication**: Automated SMS notifications to tenants.

## Tech Stack

- **Backend**: Flask 2.x, Python 3.10
- **Database**: SQLAlchemy (PostgreSQL in production, SQLite for dev)
- **Task Queue**: Celery with Redis for background processing
- **Authentication**: Flask-Login and Flask-Bcrypt
- **Frontend**: Jinja2 Templates, Vanilla CSS, and JavaScript
- **API**: REST API with Marshmallow serialization

## Project Structure

```text
venone-crm/
├── src/                # Core application source
│   ├── api/            # REST API implementation
│   ├── auth/           # Authentication and User logic
│   ├── dashboard/      # Admin, Agency, and Owner dashboards
│   ├── payment/        # Payment processing
│   ├── tenant/         # Property and Tenant management
│   ├── templates/      # Jinja2 HTML templates
│   └── static/         # Frontend assets (CSS, JS)
├── config.py           # Configuration management
├── runserver.py        # CLI application entry point
└── Pipfile             # Dependency management
```

### Docker Compose (Recommended)

If you have Docker and Docker Compose installed, you can start the entire stack with a single command:

```bash
docker compose up -d --build
```

This will:
- Build the optimized image using the multi-stage Dockerfile.
- Load environment variables from your `.env` file.
- Expose the application on `http://localhost:5000`.
- Monitor the health of the application.

To create the initial administrator:
```bash
docker compose exec app flask create-admin
```

### Manual Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd venone-crm
   ```

2. **Install dependencies**:
   Ensure you have `pipenv` installed.
   ```bash
   pipenv install
   ```

3. **Configure Environment**:
   Copy `.env.example` to `.env` and fill in the required variables (Database, SMS API, etc.).
   ```bash
   cp .env.example .env
   ```

7. **Initialize Database**:
   ```bash
   pipenv run flask init-db
   ```

8. **Create Admin User**:
   ```bash
   pipenv run flask create-admin
   ```

9. **Run the application**:
   ```bash
   pipenv run python runserver.py
   ```

## Development

- **Migrations**: Use `flask db migrate` and `flask db upgrade` to manage database changes.
- **Task Worker**: Start Celery with `celery -A src.venone.celery worker`.

## Maintenance & Database

### Emptying/Resetting the Database

**Option 1: Flask CLI (Recommended for data only)**
To drop all tables and start fresh:
```bash
# Full reset (migrations + roles)
pipenv run flask init-db

# Update roles only
pipenv run flask init-roles

# Purge tables
pipenv run flask drop-db
```

**Option 2: Docker Compose (Nuclear reset)**
To completely delete the database and its volumes:
```bash
docker compose down -v
docker compose up -d --build
```

**Option 3: Manual (SQLite only)**
Delete the local database file:
```bash
rm dev.sqlite3
```

### Seeding Test Data

To populate the database with realistic test data for development:

**Option 1: Local**
```bash
pipenv run flask seed-db --count 5
```

**Option 2: Docker**
```bash
docker compose exec app flask seed-db --count 5
```
*Note: This command currently expects `faker` to be installed in the environment.*

### CLI Management (Summary)

| Category | Shortcut (Local) | Shortcut (Docker) | Flask Command (pipenv run flask ...) |
|----------|------------------|-------------------|--------------------------------------|
| Init     | `make db-init`   | `make dk-init`    | `init-db`                            |
| Roles    | `make db-roles`  | `make dk-roles`   | `init-roles`                         |
| Admin    | `make admin`     | `make dk-admin`   | `create-admin`                       |
| Purge    | `make db-drop`   | `make dk-drop`    | `drop-db`                            |
| Seed     | `make db-seed`   | `make dk-seed`    | `seed-db`                            |

---

## Core Workflows

### 1. User & Role Hierarchy

```mermaid
graph TD
    Admin["Global Administrator"]
    Agency["Real Estate Agency"]
    Owner["House Owner"]
    Tenant["Tenant"]

    Admin -->|Manages| Agency
    Admin -->|Manages| Owner
    Agency -->|Manages| Owner
    Agency -->|Manages| Tenant
    Owner -->|Has| Tenant
    Owner -->|Owns| House["Rental Unit"]
    Tenant -->|Rents| House
```

### 2. Rental Lifecycle

```mermaid
graph LR
    CreateH[Create House] --> AssignO[Assign Owner]
    AssignO --> OpenH{House Open?}
    OpenH -- Yes --> AssignT[Assign Tenant]
    AssignT -- Set Lease Dates --> Active[Active Lease]
    Active --> RentP[Monthly Rent Payment]
    Active --> EndLease{Lease End?}
    EndLease -- No --> Active
    EndLease -- Yes --> CloseH[Close House / Eviction]
```

### 3. Payment & Automation Flow

```mermaid
sequenceDiagram
    participant T as Tenant
    participant APP as Venone App
    participant CP as CinetPay API
    participant DB as Database
    participant W as Celery Worker

    T->>APP: Initiates Payment
    APP->>DB: Create VNPayment (Status: False)
    APP->>CP: Redirect to Payment Gateway
    CP-->>T: Payment UI
    T->>CP: Authorize Payment

    Note over W, CP: Automated Verification (Every X mins)
    W->>DB: Fetch Unpaid Payments
    W->>CP: Verify Transaction Trx
    CP-->>W: Response (ACCEPTED/PENDING)
    W->>DB: Update Payment Status

    Note over APP, DB: Penalty Logic (Monthly)
    APP->>DB: Check date > 15th
    DB-->>APP: Unpaid Rents
    APP->>DB: Apply 10% Penalty
```

### 4. Alert System Logic

```mermaid
graph TD
    Check[Daily Check Loop] --> Date5{10th of Month?}
    Date5 -- Yes --> Fees[Deduct Management Fees]
    Date5 -- No --> Date15{15th of Month?}

    Date15 -- Yes --> Late{Rent Unpaid?}
    Late -- Yes --> Penalty[Apply 10% Penalty]
    Late -- Yes --> SMS[Send SMS Alert to Tenant]
    Date15 -- No --> Month3{Unpaid > 3 Months?}

    Month3 -- Yes --> Evict[Trigger Eviction Alert]
    Evict --> Notify[Notify Agency/Owner & Bailiff]
```

## Credit

Developed by [flavien-hugs](https://twitter.com/flavien_hugs)
