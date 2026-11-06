
"""Unit tests for the student management application."""

import pytest

import app


@pytest.fixture
def repository(tmp_path):
    """Provide a repository backed by a temporary database."""
    return app.StudentRepository(tmp_path / "test_students.db")


def test_add_and_get_student(repository):
    student = repository.add(
        "Aarav Mehta", "aarav@example.com", "Python", 91.0
    )

    saved_student = repository.get(student.student_id)

    assert saved_student == student


def test_list_students_returns_students_in_name_order(repository):
    repository.add("Zoya Khan", "zoya@example.com", "AWS", 80)
    repository.add("Aarav Mehta", "aarav@example.com", "Python", 91)

    students = repository.list_all()

    assert [student.name for student in students] == [
        "Aarav Mehta",
        "Zoya Khan",
    ]


def test_add_rejects_duplicate_email(repository):
    repository.add("Aarav Mehta", "aarav@example.com", "Python", 91)

    with pytest.raises(app.StudentValidationError):
        repository.add("Another Student", "aarav@example.com", "AWS", 75)


def test_get_unknown_student_raises_error(repository):
    with pytest.raises(app.StudentNotFoundError):
        repository.get(999)


def test_update_marks(repository):
    student = repository.add(
        "Diya Sharma", "diya@example.com", "Cloud", 70
    )

    updated = repository.update_marks(student.student_id, 88.5)

    assert updated.marks == 88.5


def test_update_unknown_student_raises_error(repository):
    with pytest.raises(app.StudentNotFoundError):
        repository.update_marks(999, 75)


def test_delete_student(repository):
    student = repository.add(
        "Kabir Verma", "kabir@example.com", "DevOps", 76
    )

    repository.delete(student.student_id)

    assert repository.list_all() == []


def test_delete_unknown_student_raises_error(repository):
    with pytest.raises(app.StudentNotFoundError):
        repository.delete(999)


@pytest.mark.parametrize(
    ("marks", "expected_grade"),
    [
        (95, "A"),
        (85, "B"),
        (75, "C"),
        (65, "D"),
        (45, "F"),
        (0, "F"),
    ],
)
def test_calculate_grade(marks, expected_grade):
    assert app.calculate_grade(marks) == expected_grade


@pytest.mark.parametrize("marks", [-1, 101, True, "80"])
def test_calculate_grade_rejects_invalid_marks(marks):
    with pytest.raises(app.StudentValidationError):
        app.calculate_grade(marks)


@pytest.mark.parametrize(
    ("email", "expected"),
    [
        ("student@example.com", True),
        ("student.example.com", False),
        ("student@", False),
        ("@example.com", False),
        ("student@.com", False),
    ],
)
def test_is_valid_email(email, expected):
    assert app.is_valid_email(email) is expected


def test_validate_student_details_rejects_empty_name():
    with pytest.raises(app.StudentValidationError):
        app.validate_student_details(
            " ", "student@example.com", "Python", 80
        )


def test_validate_student_details_rejects_empty_course():
    with pytest.raises(app.StudentValidationError):
        app.validate_student_details(
            "Student", "student@example.com", " ", 80
        )


def test_validate_student_details_rejects_invalid_email():
    with pytest.raises(app.StudentValidationError):
        app.validate_student_details(
            "Student", "not-an-email", "Python", 80
        )


def test_validate_student_details_rejects_invalid_marks():
    with pytest.raises(app.StudentValidationError):
        app.validate_student_details(
            "Student", "student@example.com", "Python", 101
        )


def test_validate_marks_rejects_non_numeric_value():
    with pytest.raises(app.StudentValidationError):
        app.validate_marks("excellent")


def test_print_student_report_displays_report(capsys):
    students = [
        app.Student(1, "Aarav Mehta", "aarav@example.com", "Python", 91)
    ]

    app.print_student_report(students)

    output = capsys.readouterr().out
    assert "STUDENT REPORT" in output
    assert "Aarav Mehta" in output
    assert "Class average: 91.0" in output


def test_print_student_report_handles_empty_list(capsys):
    app.print_student_report([])

    assert "No students have been registered yet." in capsys.readouterr().out


def test_load_demo_data_adds_sample_students(repository):
    app.load_demo_data(repository)

    assert len(repository.list_all()) == 3


def test_load_demo_data_does_not_duplicate_existing_data(repository):
    app.load_demo_data(repository)
    app.load_demo_data(repository)

    assert len(repository.list_all()) == 3


def test_main_runs_with_temporary_database(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(app, "DEFAULT_DATABASE", tmp_path / "main.db")

    app.main()

    output = capsys.readouterr().out
    assert "Student Management Demo" in output
    assert "STUDENT REPORT" in output
