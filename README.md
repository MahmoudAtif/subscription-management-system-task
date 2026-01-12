# Subscription Management System

A comprehensive Django REST API for managing users, subscription plans, features, and user subscriptions with analytics capabilities.

## Overview

This project is a subscription management system built with Django and Django REST Framework. It provides a complete API for managing:

- **Users**: User registration, authentication, and management
- **Features**: Individual subscription features that can be assigned to plans
- **Subscription Plans**: Plans with pricing, billing cycles, and associated features
- **User Subscriptions**: User subscription tracking with start/end dates and active status
- **Analytics**: Dashboard with revenue metrics, subscription statistics, and top users

## Features

- 🔐 Token-based authentication
- 👥 User management with signup and login
- 📦 Subscription plan management
- ⚡ Feature management and assignment
- 📊 Analytics dashboard with revenue tracking
- 🔍 Search and filtering capabilities
- 📄 Pagination for large datasets
- 📚 Interactive API documentation (Swagger/ReDoc)
- 🎯 Role-based permissions (Admin/User)
- 🗄️ PostgreSQL database support
- 📈 Data generation utility for testing

## Technology Stack

- **Django** 5.2.10
- **Django REST Framework** 3.15.2
- **PostgreSQL** (via psycopg2-binary)
- **drf-spectacular** 0.28.0 (OpenAPI/Swagger documentation)
- **django-filter** 24.3
- **Faker** 32.1.0 (for test data generation)
- **python-decouple** 3.8 (for environment variables)

## Installation Guide

### Prerequisites

- Python 3.10 or higher
- PostgreSQL database
- pip (Python package manager)

### Step 1: Clone the Repository

```bash
git clone https://github.com/MahmoudAtif/subscription-management-system-task.git
cd subscription-management-system-task
```

### Step 2: Create Virtual Environment

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the project root directory:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_ENGINE=django.db.backends.postgresql
DB_NAME=subscription_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
```

**Note**: Replace the values with your actual configuration. For production, set `DEBUG=False` and use a strong `SECRET_KEY`.

### Step 5: Set Up PostgreSQL Database

1. Create a PostgreSQL database:

```sql
CREATE DATABASE subscription_db;
```

2. Ensure PostgreSQL is running and accessible with the credentials specified in your `.env` file.

### Step 6: Run Migrations

```bash
python manage.py migrate
```

### Step 7: Create Superuser (Optional)

Create an admin user to access the Django admin panel:

```bash
python manage.py createsuperuser
```

### Step 8: Generate Test Data (Optional)

Generate sample data for testing:

```bash
# Generate default data (10,000 users, 500,000 subscriptions)
python manage.py generate_data

# Or customize the amount
python manage.py generate_data --users 1000 --subscriptions 10000 --batch-size 1000
```

### Step 9: Run the Development Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/`

## API Documentation

Once the server is running, you can access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

## API Endpoints

### Authentication

- `POST /api/users/login/` - User login (returns authentication token)
- `POST /api/users/` - User registration (public)
- `POST /api/users/logout/` - User logout

### Users

- `GET /api/users/` - List all users (authenticated)
- `GET /api/users/{id}/` - Get user details (authenticated)
- `PUT /api/users/{id}/` - Update user (authenticated)
- `PATCH /api/users/{id}/` - Partially update user (authenticated)
- `DELETE /api/users/{id}/` - Delete user (admin only)

### Features

- `GET /api/features/` - List all features (admin only)
- `GET /api/features/{id}/` - Get feature details (admin only)
- `POST /api/features/` - Create feature (admin only)
- `PUT /api/features/{id}/` - Update feature (admin only)
- `PATCH /api/features/{id}/` - Partially update feature (admin only)
- `DELETE /api/features/{id}/` - Delete feature (admin only)

### Subscription Plans

- `GET /api/plans/` - List all plans (admin only)
- `GET /api/plans/{id}/` - Get plan details (admin only)
- `POST /api/plans/` - Create plan (admin only)
- `PUT /api/plans/{id}/` - Update plan (admin only)
- `PATCH /api/plans/{id}/` - Partially update plan (admin only)
- `DELETE /api/plans/{id}/` - Delete plan (admin only)

### User Subscriptions

- `GET /api/subscriptions/` - List all subscriptions (authenticated)
- `GET /api/subscriptions/{id}/` - Get subscription details (authenticated)
- `POST /api/subscriptions/` - Create subscription (authenticated)
- `PUT /api/subscriptions/{id}/` - Update subscription (authenticated)
- `PATCH /api/subscriptions/{id}/` - Partially update subscription (authenticated)
- `DELETE /api/subscriptions/{id}/` - Delete subscription (authenticated)

### Analytics

- `GET /api/analytics/` - Get analytics dashboard data (authenticated)
  - Total recurring revenue
  - Average subscription cost
  - Monthly revenue history (last 12 months)
  - Top 5 users by subscription value
