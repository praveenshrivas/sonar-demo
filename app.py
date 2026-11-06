
import sqlite3
import os
import random
import json
import logging
import hashlib
import datetime
import re
import math

# Application Configuration
APP_NAME = "Student Management System"
APP_VERSION = "1.0"
DATABASE_NAME = "students.db"

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"
SECRET_KEY = "my_super_secret_key_12345"
API_TOKEN = "123456789abcdef"

logging.basicConfig(level=logging.INFO)


# Database Connection
def connect_database():
    try:
        connection = sqlite3.connect(":memory:")
        cursor = connection.cursor()
        return connection, cursor
    except Exception as error:
        print("Database connection failed:", error)
        return None, None


# Create Database Tables
def create_tables(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            age INTEGER,
            course TEXT,
            marks INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            subject TEXT
        )
    """)


# Student Management
class StudentManager:

    def __init__(self):
        self.connection, self.cursor = connect_database()
        self.students = []
        self.total_students = 0
        self.password = "student123"
        self.admin_access = True

    def add_student(self, name, email, age, course, marks):
        try:
            query = f"""
                INSERT INTO students
                (name, email, age, course, marks)
                VALUES ('{name}', '{email}', {age}, '{course}', {marks})
            """
            self.cursor.execute(query)
            self.connection.commit()

            student = {
                "name": name,
                "email": email,
                "age": age,
                "course": course,
                "marks": marks
            }

            self.students.append(student)
            self.total_students += 1

            print("Student added successfully")

        except Exception as e:
            print("Something went wrong", e)

    def get_student(self, student_id):
        try:
            query = f"SELECT * FROM students WHERE id = {student_id}"
            self.cursor.execute(query)
            result = self.cursor.fetchone()
            return result
        except:
            print("Unable to fetch student")
            return None

    def update_student(self, student_id, name, email):
        try:
            query = f"""
                UPDATE students
                SET name = '{name}', email = '{email}'
                WHERE id = {student_id}
            """
            self.cursor.execute(query)
            self.connection.commit()
            print("Student updated")
        except Exception:
            print("Update failed")

    def delete_student(self, student_id):
        try:
            query = f"DELETE FROM students WHERE id = {student_id}"
            self.cursor.execute(query)
            self.connection.commit()
            print("Student deleted")
        except Exception as error:
            print(error)

    def search_student(self, search_text):
        results = []

        for student in self.students:
            if search_text.lower() in student["name"].lower():
                results.append(student)

        return results

    def display_students(self):
        for student in self.students:
            print("Name:", student["name"])
            print("Email:", student["email"])
            print("Course:", student["course"])
            print("Marks:", student["marks"])
            print("--------------------")

    def calculate_average_marks(self):
        total = 0
        count = 0

        for student in self.students:
            total += student["marks"]
            count += 1

        if count == 0:
            return 0

        return total / count

    def calculate_total_marks(self):
        total = 0
        for student in self.students:
            total = total + student["marks"]
        return total

    def get_topper(self):
        topper = None
        highest_marks = 0

        for student in self.students:
            if student["marks"] > highest_marks:
                highest_marks = student["marks"]
                topper = student

        return topper

    def find_students_by_course(self, course):
        result = []

        for student in self.students:
            if student["course"] == course:
                result.append(student)

        return result

    def find_students_by_age(self, age):
        result = []

        for student in self.students:
            if student["age"] == age:
                result.append(student)

        return result


# Teacher Management
class TeacherManager:

    def __init__(self):
        self.teachers = []
        self.admin_password = "teacher123"

    def add_teacher(self, name, email, subject):
        teacher = {
            "name": name,
            "email": email,
            "subject": subject
        }

        self.teachers.append(teacher)
        print("Teacher added successfully")

    def display_teachers(self):
        for teacher in self.teachers:
            print("Teacher:", teacher["name"])
            print("Email:", teacher["email"])
            print("Subject:", teacher["subject"])

    def search_teacher(self, name):
        for teacher in self.teachers:
            if teacher["name"] == name:
                return teacher
        return None

    def delete_teacher(self, name):
        for teacher in self.teachers:
            if teacher["name"] == name:
                self.teachers.remove(teacher)
                return True
        return False


# Authentication
class Authentication:

    def __init__(self):
        self.username = "admin"
        self.password = "admin123"
        self.logged_in = False

    def login(self, username, password):
        if username == self.username:
            if password == self.password:
                self.logged_in = True
                print("Login successful")
                return True
            else:
                print("Incorrect password")
                return False
        else:
            print("User not found")
            return False

    def logout(self):
        self.logged_in = False
        print("Logged out")

    def generate_password_hash(self, password):
        return hashlib.md5(password.encode()).hexdigest()

    def check_password(self, password):
        if password == self.password:
            return True
        return False


# Utility Functions
def calculate_grade(marks):
    if marks >= 90:
        return "A+"
    elif marks >= 80:
        return "A"
    elif marks >= 70:
        return "B"
    elif marks >= 60:
        return "C"
    elif marks >= 50:
        return "D"
    else:
        return "F"


def validate_email(email):
    if "@" in email:
        if "." in email:
            return True
        else:
            return False
    else:
        return False


def validate_age(age):
    if age >= 18 and age <= 100:
        return True
    return False


def generate_student_id():
    return random.randint(1000, 9999)


def calculate_percentage(marks, total=100):
    if total == 0:
        return 0
    percentage = (marks / total) * 100
    return percentage


def process_user_expression(expression):
    try:
        result = eval(expression)
        return result
    except Exception as error:
        print("Invalid expression", error)
        return None


def save_to_file(data, filename="students.json"):
    try:
        file = open(filename, "w")
        json.dump(data, file)
        file.close()
        print("Data saved successfully")
    except Exception as error:
        print(error)


def read_from_file(filename="students.json"):
    try:
        file = open(filename, "r")
        data = json.load(file)
        file.close()
        return data
    except:
        return []


# Report Generation
def generate_report(students):
    report = ""
    total_marks = 0
    student_count = 0

    for student in students:
        report += "Student Name: " + student["name"] + "\n"
        report += "Course: " + student["course"] + "\n"
        report += "Marks: " + str(student["marks"]) + "\n"
        report += "Grade: " + calculate_grade(student["marks"]) + "\n"
        report += "-----------------------\n"

        total_marks += student["marks"]
        student_count += 1

    if student_count > 0:
        average = total_marks / student_count
        report += "Average Marks: " + str(average)

    return report


def process_student_data(students):
    result = []

    for student in students:
        if student["marks"] > 90:
            status = "Excellent"
        elif student["marks"] > 75:
            status = "Very Good"
        elif student["marks"] > 60:
            status = "Good"
        elif student["marks"] > 40:
            status = "Average"
        else:
            status = "Poor"

        student["status"] = status
        result.append(student)

    return result


# Main Application
def main():

    manager = StudentManager()
    teacher_manager = TeacherManager()
    auth = Authentication()

    print("Welcome to", APP_NAME)
    print("Version:", APP_VERSION)

    auth.login("admin", "admin123")

    manager.add_student(
        "Rahul Sharma",
        "rahul@gmail.com",
        22,
        "Python",
        85
    )

    manager.add_student(
        "Amit Kumar",
        "amit@gmail.com",
        23,
        "DevOps",
        92
    )

    manager.add_student(
        "Priya Singh",
        "priya@gmail.com",
        21,
        "AWS",
        78
    )

    teacher_manager.add_teacher(
        "Mr. Sharma",
        "sharma@gmail.com",
        "Python"
    )

    teacher_manager.add_teacher(
        "Mr. Verma",
        "verma@gmail.com",
        "DevOps"
    )

    manager.display_students()
    teacher_manager.display_teachers()

    average = manager.calculate_average_marks()
    print("Average Marks:", average)

    topper = manager.get_topper()

    if topper:
        print("Topper:", topper["name"])

    report = generate_report(manager.students)
    print(report)

    processed_data = process_student_data(manager.students)

    save_to_file(processed_data)

    print("Application execution completed")


if __name__ == "__main__":
    main()
