## **Documentation for To-Do List Application**

### **1. Overview**
The To-Do List application is a Django-based project that allows users to manage their daily tasks efficiently.  
#### **Key Features**:
- Add, update, and delete tasks.
- Mark tasks as completed or incomplete.
- Browse and interact with APIs using the Django REST Framework's browsable interface.

---

### **2. Setup Instructions**
#### **Prerequisites**:
- Python 3.10+
- Pip (Python package installer)

#### **Steps**:
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/vishwa-glitch/Todo
   cd todolist
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Start the Server**:
   ```bash
   python manage.py runserver
   ```
   Access the application at `http://127.0.0.1:8000/`.

---

### **3. Testing**
#### **Run Tests**:
- Unit Tests:
  ```bash
  python manage.py test core.tests.unit
  ```
- Integration Tests:
  ```bash
  python manage.py test core.tests.integration
  ```
- End-to-End Tests:
  ```bash
  python manage.py test core.tests.test_e2e
  ```

#### **Generate Coverage Reports**:
1. Install coverage:
   ```bash
   pip install coverage
   ```
2. Run tests with coverage:
   ```bash
   coverage run manage.py test
   coverage html
   ```
3. Open the coverage report:
   ```bash
   open htmlcov/index.html
   ```

---

### **4. Deployment**
The application is deployed on **PythonAnywhere**.  
#### **Access the App**:
- **Main URL**: [To-Do List Application](https://vishwa55.pythonanywhere.com)  
- **REST API Browsable Interface**: [API Endpoint](https://vishwa55.pythonanywhere.com/core/api/)

---

### **6. Postman Collection**
The API endpoints for the To-Do List application are documented in a public Postman collection.  
#### **Access the Collection**:
[Postman Collection Link](https://www.postman.com/vishwa1234567/algobulls-backend-developer-web-coding-assignment/collection/f4dfe1c/todo-api-crud-operations?action=share&creator=38966661)

#### **Endpoints**:
- **`GET /core/api/todos/`**: Retrieve all tasks.
- **`POST /core/api/todos/`**: Create a new task.
- **`PUT /core/api/todos/`**: Update a task.
- **`DELETE /core/api/todos/`**: Delete a task.

---