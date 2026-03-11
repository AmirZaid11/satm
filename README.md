# SATM (School Analytics & Timetabling Management)

A Django-based application for school management, featuring advanced timetabling algorithms, role-based access control (RBAC), and analytics dashboards. This project utilizes Google OR-Tools for complex school schedule generation and features a modern administrative interface via `django-unfold`.

## Technical Stack
- **Backend Framework**: Django 6.0
- **Database Backend**: MySQL (via `mysqlclient`) / SQLite3 (dev)
- **Algorithms**: Google OR-Tools (`ortools`)
- **Data Processing**: Pandas & NumPy
- **Frontend / UI**: Tailwind CSS
- **Admin Interface**: Django Unfold

## Project Structure
- **satm_core**: Core project settings and configurations.
- **analytics**: Sub-app for handling school data insights and dashboards.
- **timetabling**: Sub-app integrating OR-Tools for automated schedule generation.
- **users**: Sub-app handling user profiles and RBAC.

## Setup Instructions

### 1. Python Environment Setup
Create a Python virtual environment and install the required dependencies:
```bash
python -m venv venv
# On Unix or MacOS
source venv/bin/activate
# On Windows
venv\Scripts\activate

# Install Python requirements
pip install -r requirements.txt
```

### 2. Database Migrations
Configure your database connection in `satm_core/settings.py` (or through environment variables), then run the migrations:
```bash
python manage.py migrate
```

### 3. Frontend / Static Files Setup
To build or compile the Tailwind CSS styles, make sure Node.js is installed, then run:
```bash
npm install
# To watch for CSS changes
npm run watch
# To build CSS for production
npm run build:css
```

### 4. Admin Setup & Data Seeding
Create an administrative user by running:
```bash
python manage.py createsuperuser
```
The project also comes with several data-seeding and debug scripts:
- `seed_data.py`: Populate the database with initial application data.
- `generate_test_students.py`: Generates dummy student datasets.
- `check_db.py` / `inspect_schema.py` / `verify_rbac.py` : Scripts for validating state.

### 5. Running the Application
Spin up the Django development server:
```bash
python manage.py runserver
```

You can now navigate to `http://127.0.0.1:8000/` and access the admin panel at `http://127.0.0.1:8000/admin/`.
