## **📋 Documentation for To-Do List Application**

### **1. Overview**
The **To-Do List Application** is a Django-based backend project that enables users to manage their daily tasks efficiently. This project was developed as part of a backend developer assignment, adhering to all specified requirements.

#### **Key Features**:
- **Task Management**:
  - Add, update, and delete tasks.
  - Manage task details, such as title, description, due date, tags, and status.
- **Task Status Tracking**:
  - Track tasks through various statuses: OPEN, WORKING, PENDING REVIEW, COMPLETED, OVERDUE, and CANCELLED.
- **Django Admin Integration**:
  - Enhanced admin panel with filters and fieldsets for easier task management.
- **REST API**:
  - Full CRUD (Create, Read, Update, Delete) functionality for tasks using Django REST Framework.
- **Authentication**:
  - Secured APIs with Basic Authentication.
- **Testing**:
  - Comprehensive unit, integration, and end-to-end tests with 100% coverage.
- **CI/CD Integration**:
  - Automated GitHub Actions for running tests and linting (Flake8 and Black).
- **Documentation**:
  - Full code documentation hosted as a static site.
- **E2E Test Recordings**:
  - Video recordings of end-to-end tests available in the `videos` folder.

---

### **2. Setup Instructions**

#### **Prerequisites**:
- Python 3.11+
- Pip (Python package installer)
- Virtual environment (optional but recommended)

#### **Steps**:
1. **Clone the Repository**:

   ```bash
   git clone https://github.com/vishwa-glitch/Todo
   cd Todo
   ```

2. **Set Up a Virtual Environment (Optional)**:
   
   ```bash
   python -m venv venv
   source venv/bin/activate   # For Linux/macOS
   venv\Scripts\activate      # For Windows
   ```

3. **Install Dependencies**:
   
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Migrations**:
   
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Start the Server**:
   
   ```bash
   python manage.py runserver
   ```

   Access the application at **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**.

---

### **3. Testing**

#### **Run Tests**:
- **Unit Tests**:
  
  ```bash
  python manage.py test core.tests.unit
  ```

- **Integration Tests**:
  
  ```bash
  python manage.py test core.tests.integration
  ```

- **End-to-End Tests**:
  
  ```bash
  python manage.py test core.tests.test_e2e
  ```

#### **Generate Coverage Reports**:
1. Install Coverage:

   ```bash
   pip install coverage
   ```

2. Run Tests with Coverage:

   ```bash
   coverage run manage.py test
   coverage html
   ```

3. Open the Coverage Report:

   ```bash
   open htmlcov/index.html  # Linux/macOS
   start htmlcov/index.html # Windows
   ```

#### **E2E Test Recordings**:
- End-to-end test recordings are available in the `videos` folder. 📂

---

### **4. Deployment**
The application is deployed on **PythonAnywhere**. Access the live version [here](#).

---

### **5. CI/CD Integration**
This project uses **GitHub Actions** to automate:
- Running unit, integration, and end-to-end tests on every commit.
- Linting the codebase with Flake8 and formatting with Black to ensure PEP8 compliance.

---

### **6. Features Implemented**:
- **Task Management**:
  - Add, update, delete, and retrieve tasks.
  - Ensure tasks have timestamps, titles, descriptions, due dates, tags, and statuses.
- **Validation**:
  - Prevent invalid operations (e.g., due dates earlier than creation timestamps).
  - Ensure uniqueness for multiple tags on the same task.
- **Admin Interface**:
  - Filter and manage tasks directly from Django Admin.
- **Postman Collection**:
  - A working Postman Collection is shared to test all APIs.

---

### **7. Screenshot**
[Coverage report]

![image](https://github.com/user-attachments/assets/119d666b-1a42-4d6f-a9d4-019cb6f30771)
