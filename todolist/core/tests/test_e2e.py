import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

class E2ETestCase(LiveServerTestCase):
    def setUp(self):
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        self.driver.implicitly_wait(10)

    def test_create_todo_item(self):
        """Todo item successfully created"""
        self.driver.get(f"{self.live_server_url}/core/todo-app/")
        time.sleep(1)  # Pause to show page load

        # Locate input fields
        title_input = self.driver.find_element(By.ID, "title")
        description_input = self.driver.find_element(By.ID, "description")
        submit_button = self.driver.find_element(By.ID, "submitButton")

        # Slow down input
        title_input.send_keys("Test Task")
        time.sleep(0.5)  # Pause between inputs
        description_input.send_keys("This is a test task.")
        time.sleep(0.5)  # Pause before submission

        # Submit and pause to show action
        submit_button.click()
        time.sleep(1)  # Pause to show submission result

        # Verify creation
        self.assertIn("Test Task", self.driver.page_source)

    def test_view_todo_items(self):
        """Multiple todo items displayed"""
        # Open the application
        self.driver.get(f"{self.live_server_url}/core/todo-app/")
        time.sleep(1)  # Pause to show page load

        # Locate input fields
        title_input = self.driver.find_element(By.ID, "title")
        description_input = self.driver.find_element(By.ID, "description")
        submit_button = self.driver.find_element(By.ID, "submitButton")

        # Slow down input
        title_input.send_keys("Test Task")
        time.sleep(0.5)
        description_input.send_keys("This is a test task.")
        time.sleep(0.5)

        # Submit and pause
        submit_button.click()
        time.sleep(1)  # Pause to show todo creation

        # Wait for todo to render
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "todoList"),
                "Test Task"
            )
        )

        # Additional pause to show list
        time.sleep(1)

        # Verify
        self.assertIn("Test Task", self.driver.page_source)

    def test_update_todo_item(self):
        """Todo item successfully updated"""
        # Open the application
        self.driver.get(f"{self.live_server_url}/core/todo-app/")
        time.sleep(1)  # Pause to show page load

        # Create initial todo
        title_input = self.driver.find_element(By.ID, "title")
        description_input = self.driver.find_element(By.ID, "description")
        submit_button = self.driver.find_element(By.ID, "submitButton")

        title_input.send_keys("Test Task")
        time.sleep(0.5)
        description_input.send_keys("This is a test task.")
        time.sleep(0.5)
        submit_button.click()
        time.sleep(1)  # Pause after creation

        # Find and click edit button
        edit_button = self.driver.find_element(By.XPATH, "//button[text()='Edit']")
        edit_button.click()
        time.sleep(1)  # Pause to show edit mode

        # Edit the task
        title_input = self.driver.find_element(By.ID, "title")
        title_input.clear()
        time.sleep(0.5)
        title_input.send_keys("Updated Test Task")
        time.sleep(0.5)

        # Submit update
        submit_button = self.driver.find_element(By.ID, "submitButton")
        submit_button.click()
        time.sleep(1)  # Pause to show update result

        # Verify update
        self.assertIn("Updated Test Task", self.driver.page_source)

    def test_delete_todo_item(self):
        """Todo item successfully deleted"""
        # Open the application
        self.driver.get(f"{self.live_server_url}/core/todo-app/")
        time.sleep(1)  # Pause to show page load

        # Create todo to delete
        title_input = self.driver.find_element(By.ID, "title")
        description_input = self.driver.find_element(By.ID, "description")
        submit_button = self.driver.find_element(By.ID, "submitButton")

        title_input.send_keys("Test Task")
        time.sleep(0.5)
        description_input.send_keys("This is a test task.")
        time.sleep(0.5)
        submit_button.click()
        time.sleep(1)  # Pause after creation

        # Find and click delete button
        delete_button = self.driver.find_element(By.XPATH, "//button[text()='Delete']")
        delete_button.click()
        time.sleep(1)  # Pause to show deletion

        # Verify deletion
        self.assertNotIn("Test Task", self.driver.page_source)

    def tearDown(self):
        if hasattr(self, 'driver'):
            self.driver.quit()