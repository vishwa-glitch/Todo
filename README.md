# Todo List Django Application

## Project Overview
A Django-based Todo List application developed for AlgoBulls Backend Developer Internship.

## Features
- Create, Read, Update, Delete Todo Items
- Django Admin Interface
- REST API Endpoints
- Authentication Support

## Technology Stack
- Python 3.11+
- Django 4.2.7+
- Django Rest Framework 3.14.0+

## Setup Instructions

### Prerequisites
- Python 3.11+
- pip
- virtualenv (recommended)

### Installation Steps
1. Clone the repository
   ```bash
   git clone https://github.com/vishwa-glitch/todo
   cd todo
   ```

2. Create Virtual Environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install Dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Database Setup
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. Run Development Server
   ```bash
   python manage.py runserver
   ```

## Running Tests
```bash
# Run Unit Tests and # Run Integration Tests
python manage.py test tests
```

# Install coverage
```bash
pip install coverage

# Run tests with coverage
coverage run --source='.' manage.py test
coverage html  # Generate HTML report
coverage report  # Print report to console
```
## Coverage Report
![image](https://github.com/user-attachments/assets/f77c29c0-d89b-4ad1-a1a1-4566c346c5b8)



## Contact
- Email: [vishwa12550@gmail.com]
