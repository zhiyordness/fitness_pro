# Fitness Pro

A Django-based web application for managing **training programs, nutrition planning, and progress tracking** in one structured system.

Fitness Pro allows users to:

- Organize training splits by muscle groups
- Browse and manage an exercise library
- Plan daily meals with macro calculations
- Track body measurements and weight progress
- Upload progress images
- View a dashboard overview of training, nutrition, and progress

---

# Project Overview

Fitness Pro is built as a modular Django application that demonstrates:

- Clean architecture and app separation
- Relational database design with normalized models
- Many-to-One and Many-to-Many relationships
- Form validation and customization
- Full CRUD functionality
- Template inheritance and reusable components
- Query optimization using `prefetch_related` and `annotate`
- Custom template filters
- Management commands for database population

The project follows Django best practices and Object-Oriented Programming principles.

---

# Project Structure

The application consists of four Django apps:

### 1. `training`
Manages:
- Training days (splits)
- Muscle groups
- Muscles
- Exercises

### 2. `nutrition`
Manages:
- Nutrition days
- Meals
- Food database
- Meal-food relationships
- Macro calculations

### 3. `progress`
Manages:
- Weight tracking
- Body measurements
- Progress images

### 4. `common`
Contains:
- Base templates
- Navigation
- Homepage dashboard
- Custom 404 page

---

# Business Logic

The project separates business logic from view logic where appropriate.

## NutritionCalculator Service Class

The `NutritionCalculator` class is responsible for calculating:

- Total macronutrients per meal
- Total macronutrients per day

This ensures:

- Clean separation of concerns
- Reusable logic
- Thin views
- Better maintainability

### Meal Total Calculation

For each `MealFoodItem`, the calculator:

1. Adjusts quantity based on measurement (grams, pieces, milliliters)
2. Multiplies the quantity by the nutritional values of the related `FoodDatabase` entry
3. Aggregates totals for:
   - Calories
   - Protein
   - Carbohydrates
   - Fat

### Day Total Calculation

For each `NutritionDay`, the calculator:

1. Iterates through all related meals
2. Calculates individual meal totals
3. Aggregates them into daily totals

---

## Homepage Dashboard Aggregation

The homepage combines data from all modules and dynamically displays:

- Today’s training split
- Assigned exercises and muscle groups
- Next scheduled meal for the day
- Total calories for the next meal
- Latest progress record
- Weight change compared to previous record

This demonstrates cross-app integration and real-world dashboard logic.

---

## Query Optimization

The project uses:

- `prefetch_related()` for Many-to-Many optimization
- `annotate()` with `Case` and `When` for weekday ordering
- Efficient queryset handling in ListViews
- Pagination for large datasets

This ensures:

- Reduced database queries
- Better performance
- Scalable structure

---


# Technologies Used

- Python 3.x
- Django 6.0.1
- PostgreSQL
- Bootstrap 5
- Pillow
- django-unfold
- python-dotenv

---

# Setup & Installation

## 1. Clone the Repository

```bash
git clone <your-repo-url>
cd fitness_pro
```

## 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file in the project root:

```
SECRET_KEY=your-secret-key
DB_NAME=fitness_pro_db
DB_USER=your_db_user
DB_PASS=your_db_password
DB_HOST=localhost
DB_PORT=5432
```

---

# PostgreSQL Setup

Create a PostgreSQL database:

```sql
CREATE DATABASE fitness_pro_db;
```

---

# Apply Migrations

```bash
python manage.py migrate
```

---

# Populate Initial Data (Optional)

Training data:

```bash
python manage.py populate_training
```

Food database:

```bash
python manage.py populate_foods
```

---

# Run the Application

```bash
python manage.py runserver
```

Open in browser:

```
http://127.0.0.1:8000/
```

---

# Features Overview

### Training Module
- Create training days
- Assign muscle groups
- Select exercises dynamically
- Full CRUD functionality

### Exercise Library
- Search functionality
- Pagination
- Detailed exercise view

### Nutrition Module
- Create days and meals
- Add food items to meals
- Automatic macro calculation
- Daily totals overview

### Progress Tracker
- Record body measurements
- Upload progress images
- View detailed progress history
- Pagination

---

# Security

- Environment variables for sensitive data
- CSRF protection enabled (Django default middleware)
- PostgreSQL backend for secure and reliable data management

---

# Author

Zhivomir Yordanov
