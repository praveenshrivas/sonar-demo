
"""Student Management application for a SonarQube demonstration."""

from __future__ import annotations

import logging
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

LOGGER = logging.getLogger(__name__)
DEFAULT_DATABASE = Path("students.db")


class StudentNotFoundError(LookupError):
    """Raised when a requested student does not exist."""


class StudentValidationError(ValueError):
    """Raised when student details are invalid."""


@dataclass(frozen=True)
class Student:
    """Represent a student record."""

    student_id: int
    name: str
    email: str
    course: str
    marks: float


class StudentRepository:
    """Handle persistence of student records in SQLite."""

    def __init__(self, database_path: Path = DEFAULT_DATABASE) -> None:
        self._database_path = database_path
        self._initialize_database()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize_database(self) -> None:
        query = """
            CREATE TABLE IF NOT EXISTS students (
                student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                course TEXT NOT NULL,
                marks REAL NOT NULL CHECK (marks >= 0 AND marks <= 100)
            )
        """
        with self._connect() as connection:
            connection.execute(query)

    def add(self, name: str, email: str, course: str, marks: float) -> Student:
        validate_student_details(name, email, course, marks)
        query = """
            INSERT INTO students (name, email, course, marks)
            VALUES (?, ?, ?, ?)
        """
        try:
            with self._connect() as connection:
                cursor = connection.execute(
                    query, (name, email, course, marks)
                )
                student_id = cursor.lastrowid
        except sqlite3.IntegrityError as error:
            LOGGER.warning("Could not add student with email %s", email)
            raise StudentValidationError(
                "A student with this email address already exists."
            ) from error

        if student_id is None:
            raise RuntimeError("The database did not return a student ID.")

        return Student(student_id, name, email, course, marks)

    def get(self, student_id: int) -> Student:
        query = """
            SELECT student_id, name, email, course, marks
            FROM students
            WHERE student_id = ?
        """
        with self._connect() as connection:
            row = connection.execute(query, (student_id,)).fetchone()

        if row is None:
            raise StudentNotFoundError(
                f"Student {student_id} was not found."
            )
        return student_from_row(row)

    def list_all(self) -> list[Student]:
        query = """
            SELECT student_id, name, email, course, marks
            FROM students
            ORDER BY name COLLATE NOCASE
        """
        with self._connect() as connection:
            rows = connection.execute(query).fetchall()

        return [student_from_row(row) for row in rows]

    def update_marks(self, student_id: int, marks: float) -> Student:
        validate_marks(marks)
        query = "UPDATE students SET marks = ? WHERE student_id = ?"

        with self._connect() as connection:
            cursor = connection.execute(query, (marks, student_id))
            if cursor.rowcount == 0:
                raise StudentNotFoundError(
                    f"Student {student_id} was not found."
                )

        return self.get(student_id)

    def delete(self, student_id: int) -> None:
        query = "DELETE FROM students WHERE student_id = ?"

        with self._connect() as connection:
            cursor = connection.execute(query, (student_id,))
            if cursor.rowcount == 0:
                raise StudentNotFoundError(
                    f"Student {student_id} was not found."
                )


def student_from_row(row: sqlite3.Row) -> Student:
    return Student(
        student_id=int(row["student_id"]),
        name=str(row["name"]),
        email=str(row["email"]),
        course=str(row["course"]),
        marks=float(row["marks"]),
    )


def validate_student_details(
    name: str, email: str, course: str, marks: float
) -> None:
    if not name.strip():
        raise StudentValidationError("Student name cannot be empty.")
    if not course.strip():
        raise StudentValidationError("Course name cannot be empty.")
    if not is_valid_email(email):
        raise StudentValidationError("Enter a valid email address.")
    validate_marks(marks)


def validate_marks(marks: float) -> None:
    if not isinstance(marks, (int, float)) or isinstance(marks, bool):
        raise StudentValidationError("Marks must be a number.")
    if not 0 <= marks <= 100:
        raise StudentValidationError("Marks must be between 0 and 100.")


def is_valid_email(email: str) -> bool:
    value = email.strip()
    if value.count("@") != 1:
        return False

    local_part, domain = value.split("@")
    return bool(local_part and "." in domain and not domain.startswith("."))


def calculate_grade(marks: float) -> str:
    validate_marks(marks)

    grade_boundaries: Sequence[tuple[float, str]] = (
        (90, "A"),
        (80, "B"),
        (70, "C"),
        (60, "D"),
        (0, "F"),
    )

    for minimum_mark, grade in grade_boundaries:
        if marks >= minimum_mark:
            return grade

    return "F"


def print_student_report(students: Sequence[Student]) -> None:
    if not students:
        print("No students have been registered yet.")
        return

    print("\nSTUDENT REPORT")
    print("-" * 72)
    print(f"{'ID':<6}{'NAME':<22}{'COURSE':<18}{'MARKS':>8}{'GRADE':>8}")
    print("-" * 72)

    for student in students:
        grade = calculate_grade(student.marks)
        print(
            f"{student.student_id:<6}"
            f"{student.name[:20]:<22}"
            f"{student.course[:16]:<18}"
            f"{student.marks:>8.1f}"
            f"{grade:>8}"
        )

    average = sum(student.marks for student in students) / len(students)
    print("-" * 72)
    print(f"Class average: {average:.1f}")


def load_demo_data(repository: StudentRepository) -> None:
    if repository.list_all():
        return

    sample_students = (
        ("Aarav Mehta", "aarav@example.com", "Python", 91.0),
        ("Diya Sharma", "diya@example.com", "Cloud Computing", 84.5),
        ("Kabir Verma", "kabir@example.com", "DevOps", 76.0),
    )

    for details in sample_students:
        try:
            repository.add(*details)
        except StudentValidationError:
            LOGGER.info("Skipping an existing sample student.")


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    repository = StudentRepository()
    load_demo_data(repository)
    students = repository.list_all()

    print(f"Welcome to the Student Management Demo ({len(students)} students)")
    print_student_report(students)


if __name__ == "__main__":
    main()
