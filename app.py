                    f"Student {student_id} was not found."
                )


def student_from_row(row: sqlite3.Row) -> Student:
    """Convert a SQLite row into a Student value object."""
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
    """Validate the fields required to create a student."""
    if not name.strip():
        raise StudentValidationError("Student name cannot be empty.")
    if not course.strip():
        raise StudentValidationError("Course name cannot be empty.")
    if not is_valid_email(email):
        raise StudentValidationError("Enter a valid email address.")
    validate_marks(marks)


def validate_marks(marks: float) -> None:
    """Ensure marks are a number between zero and one hundred."""
    if not isinstance(marks, (int, float)) or isinstance(marks, bool):
        raise StudentValidationError("Marks must be a number.")
    if not 0 <= marks <= 100:
        raise StudentValidationError("Marks must be between 0 and 100.")


def is_valid_email(email: str) -> bool:
    """Perform a basic email format check suitable for this demo."""
    value = email.strip()
    if value.count("@") != 1:
        return False
    local_part, domain = value.split("@")
    return bool(local_part and "." in domain and not domain.startswith("."))


def calculate_grade(marks: float) -> str:
    """Convert a mark percentage into a letter grade."""
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
    """Print a readable report for a collection of students."""
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
    """Add sample students when the database is empty."""
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
    """Run the student management demonstration."""
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
