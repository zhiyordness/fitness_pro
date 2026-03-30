# Fitness Pro

A Django-based web application for managing **training programs, nutrition planning, and progress tracking** in one structured system.


---

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Local Development Setup](#local-development-setup)
- [Environment Variables](#environment-variables)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [Testing](#testing)
- [Project Structure](#project-structure)


---

## Project Overview

Fitness Pro is a full-featured fitness management platform that allows users to:
- Track workouts and exercises
- Log nutrition and food intake
- Monitor fitness progress over time
- Create custom workout routines
- Access a comprehensive exercise library
- Manage food database

The application includes both public and private sections, with role-based permissions for content editors.
---

## Features

### Core Functionality
-  User registration and authentication
-  Email verification for new accounts
-  Profile management with fitness goals
-  Exercise library with search and filter
-  Food database with nutritional information
-  Workout creation and tracking
-  Progress monitoring with charts
-  Full CRUD operations for owners

### Technical Features
-  Class-based views (90% CBV usage)
-  RESTful API using Django REST Framework
-  Asynchronous tasks with Celery
-  Redis caching for performance
-  PostgreSQL database with SSL
-  Responsive Bootstrap design
-  Comprehensive test suite
-  Production-ready security features

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Django 5.1.3, Python 3.12 |
| **Database** | PostgreSQL 14 (Azure Flexible Server) |
| **Cache/Broker** | Redis 7.0 |
| **Task Queue** | Celery 5.6 |
| **API** | Django REST Framework 3.15 |
| **Frontend** | Bootstrap 5, HTML5, CSS3 |
| **Deployment** | Microsoft Azure App Service |
| **Static Files** | WhiteNoise |
| **Async Tasks** | Celery + Redis |
| **Email** | SMTP (Gmail/SendGrid) |

---

## Architecture
┌─────────────────────────────────────┐
│         Azure App Service           │
│                                     │
│    ┌───────────────────────────┐    │
│    │      Gunicorn Server      │    │
│    │                           │    │
│    │   ┌───────────────────┐   │    │
│    │   │  Django App       │   │    │
│    │   │                   │   │    │
│    │   │  - Accounts       │   │    │
│    │   │  - Training       │   │    │
│    │   │  - Nutrition      │   │    │
│    │   │  - Progress       │   │    │
│    │   │  - Common         │   │    │
│    │   │  - API            │   │    │
│    │   └───────────────────┘   │    │
│    └───────────────────────────┘    │
└─────────────┬───────────────────────┘
              │
    ┌─────────┼─────────┐
    ▼         ▼         ▼
┌────────┐ ┌──────┐ ┌────────┐
│Postgres│ │Redis │ │ Blob   │
│Database│ │Cache │ │Storage │
└────────┘ └──────┘ └────────┘

---

## Prerequisites

- Python 3.12 or higher
- PostgreSQL 14 or higher (local development)
- Redis 7.0 (optional, for Celery)
- Git
- Azure CLI (for deployment)
- Virtual environment tool (venv)
- Cloudinary
---

## Local Development Setup

### 1. Clone the Repository
```bash
git clone https://github.com/zhiyordness/fitness_pro.git
cd fitness_pro
````

### 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Create Environment File

Create a .env file in the project root or use .env.example in the project:

```bash
cp .env.example .env
```

### 5. Configure Database

Create a PostgreSQL database:

```sql
CREATE DATABASE fitness_pro;
CREATE USER fitness_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE fitness_pro TO fitness_user;
```

### 6. Run Migrations

```bash
python manage.py migrate
```

### 7. Create Superuser

```bash
python manage.py createsuperuser
```

### 8. Collect Static Files

```bash
python manage.py collectstatic
```

### 9. Run Development Server

```bash
python manage.py runserver
```

Access the application at: http://localhost:8000

---

# Environment Variables

Create a `.env` file in the project root or use the .env.example template in the project:

```
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

.
.
.
```
---

## PostgreSQL Database Setup

Create a PostgreSQL database:

```sql
CREATE DATABASE fitness_pro_db;
```

### Apply Migrations

```bash
python manage.py migrate
```

### Populate Initial Data (Optional)

Training data:

```bash
python manage.py populate_training_data
```

Food database:

```bash
python manage.py populate_food_database
```

---
## Running the Application

### Development Server

```bash
python manage.py runserver
```

### Production with Gunicorn

```bash
gunicorn --workers 3 --bind 0.0.0.0:8000 fitness_pro.wsgi:application
```

### Celery Worker (Async Tasks)

```bash
celery -A fitness_pro worker --loglevel=info
```

### Run Tests

```bash
python manage.py test
```
---

## Testing

The project includes a comprehensive test suite covering:
- Model tests for all apps
- View tests for key endpoints
- Form validation tests
- API endpoint tests

Run tests with:

```bash
python manage.py test
``` 
---

## Project Structure

```
fitness_pro/
├── fitness_pro/              # Project configuration
│   ├── settings.py          # Development settings
│   ├── azure_settings.py    # Production settings
│   ├── urls.py              # Main URL configuration
│   └── wsgi.py              # WSGI entry point
├── accounts/                 # User management app
│   ├── models.py            # User and Profile models
│   ├── views.py             # Registration, login, profile views
│   ├── forms.py             # User forms
│   └── urls.py              # Authentication URLs
├── training/                 # Workout and exercise app
│   ├── models.py            # Exercise, Workout models
│   ├── views.py             # Workout CRUD views
│   └── forms.py             # Workout forms
├── nutrition/                # Food tracking app
│   ├── models.py            # Food, Meal models
│   ├── views.py             # Food database views
│   └── forms.py             # Food entry forms
├── progress/                 # Progress tracking app
│   ├── models.py            # Progress, Statistics models
│   └── views.py             # Progress charts and stats
├── common/                   # Shared utilities
│   ├── middleware.py        # Rate limiting, custom middleware
│   └── context_processors.py # Global template variables
├── api/                      # REST API
│   ├── serializers.py       # DRF serializers
│   ├── views.py             # API views
│   └── urls.py              # API endpoints
├── static/                   # Static files
│   ├── css/                 # Stylesheets
│   ├── js/                  # JavaScript files
│   └── images/              # Images and icons
├── templates/                # HTML templates
│   ├── base.html            # Base template
│   ├── common/              # Shared templates
│   └── accounts/            # User-related templates
├── media/                    # User-uploaded files
├── requirements.txt          # Python dependencies
├── runtime.txt               # Python version for Azure
├── .env.example              # Environment variables template
├── manage.py                 # Django management script
└── README.md                 # This file
```
---
 
## Author

### Zhivomir Yordanov - @zhiyordness


## Acknowledgments

- Django Software Foundation
- Microsoft Azure for hosting
- Bootstrap team for the CSS framework
- ll contributors and testers

---

## Links

### Live Application: https://fitnesspro-arhfd9ftcng6dbcr.polandcentral-01.azurewebsites.net/
### GitHub Repository: https://github.com/zhiyordness/fitness_pro

