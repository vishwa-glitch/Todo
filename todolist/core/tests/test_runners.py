from django.test.runner import DiscoverRunner
from unittest import TestResult
import sys
import time

from unittest import TestResult

class CustomTestResult(TestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.start_time = time.time()

    def startTest(self, test):
        super().startTest(test)  # Ensure base functionality is retained
        self.total_tests += 1
        print(f"TestCase: {test._testMethodName}", end=" ")

    def addSuccess(self, test):
        super().addSuccess(test)  # Ensure base functionality is retained
        self.passed_tests += 1
        print("\033[92m✓ PASS:\033[0m", end=" ")
        print(f"{test._testMethodDoc or 'Test completed successfully'}")

    def addError(self, test, err):
        super().addError(test, err)  # Ensure base functionality is retained
        self.failed_tests += 1
        print("\033[91m✗ ERROR:\033[0m", test._testMethodName)
        print(f"Error details: {err[1]}")

    def addFailure(self, test, err):
        super().addFailure(test, err)  # Ensure base functionality is retained
        self.failed_tests += 1
        print("\033[91m✗ FAIL:\033[0m", test._testMethodName)
        print(f"Failure details: {err[1]}")

    def printSummary(self):
        end_time = time.time()
        duration = end_time - self.start_time

        print("\n\033[1mTest Summary:\033[0m")
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Duration: {duration:.2f} seconds")


class CustomTestRunner(DiscoverRunner):
    def run_suite(self, suite, **kwargs):
        result = CustomTestResult()
        suite.run(result)
        result.printSummary()
        return result