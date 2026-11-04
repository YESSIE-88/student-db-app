import os
import sys
from contextlib import contextmanager
from datetime import datetime, date

import psycopg2
from psycopg2 import errors


# ---------------------------------------------------------------------------
# Database connection functions
# ---------------------------------------------------------------------------

def get_connection():
    """Create and return a new PostgreSQL connection using environment variables."""
    return psycopg2.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=os.getenv("PGPORT", "5432"),
        dbname=os.getenv("PGDATABASE", "student_db"),
        user=os.getenv("PGUSER", "postgres"),
        password=os.getenv("PGPASSWORD", ""),
    )


@contextmanager
def db_cursor(commit: bool = False):
    """
    Provide a database cursor.

    - Commits if commit=True and no exception occurs.
    - Rolls back if an exception occurs.
    - Always closes the connection.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            yield cur
        if commit:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Application functions
# ---------------------------------------------------------------------------

def getAllStudents() -> None:
    """Retrieve and display all records from the students table."""
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT student_id, first_name, last_name, email, enrollment_date
            FROM students
            ORDER BY student_id;
            """
        )
        rows = cur.fetchall()

    if not rows:
        print("No student records found.")
        return

    print()
    print(f"{'ID':<6} {'First Name':<15} {'Last Name':<15} {'Email':<32} {'Enrollment Date':<15}")
    print("-" * 90)

    for student_id, first_name, last_name, email, enrollment_date in rows:
        date_text = enrollment_date.isoformat() if enrollment_date else ""
        print(
            f"{student_id:<6} {first_name:<15} {last_name:<15} "
            f"{email:<32} {date_text:<15}"
        )


def addStudent(first_name: str, last_name: str, email: str, enrollment_date: date) -> None:
    """Insert a new student record and display the generated student_id."""
    with db_cursor(commit=True) as cur:
        cur.execute(
            """
            INSERT INTO students (first_name, last_name, email, enrollment_date)
            VALUES (%s, %s, %s, %s)
            RETURNING student_id;
            """,
            (first_name.strip(), last_name.strip(), email.strip(), enrollment_date),
        )
        new_id = cur.fetchone()[0]

    print(f"Student added successfully with student_id={new_id}.")


def updateStudentEmail(student_id: int, new_email: str) -> None:
    """Update the email address for the student with the given student_id."""
    with db_cursor(commit=True) as cur:
        cur.execute(
            """
            UPDATE students
            SET email = %s
            WHERE student_id = %s
            RETURNING student_id;
            """,
            (new_email.strip(), student_id),
        )
        updated = cur.fetchone()

    if updated:
        print(f"Email updated for student_id={student_id}.")
    else:
        print(f"No student found with student_id={student_id}.")


def deleteStudent(student_id: int) -> None:
    """Delete the student with the given student_id."""
    with db_cursor(commit=True) as cur:
        cur.execute(
            """
            DELETE FROM students
            WHERE student_id = %s
            RETURNING student_id;
            """,
            (student_id,),
        )
        deleted = cur.fetchone()

    if deleted:
        print(f"Student with student_id={student_id} deleted.")
    else:
        print(f"No student found with student_id={student_id}.")


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def prompt_int(prompt: str) -> int:
    """Prompt until the user enters a valid integer."""
    while True:
        try:
            return int(input(prompt).strip())
        except ValueError:
            print("Please enter a valid integer.")


def prompt_date(prompt: str) -> date:
    """Prompt until the user enters a valid date in YYYY-MM-DD format."""
    while True:
        text = input(prompt).strip()
        try:
            return datetime.strptime(text, "%Y-%m-%d").date()
        except ValueError:
            print("Invalid date. Please use YYYY-MM-DD.")


def prompt_nonempty(prompt: str) -> str:
    """Prompt until the user enters a non-empty value."""
    while True:
        text = input(prompt).strip()
        if text:
            return text
        print("This value cannot be empty.")


def print_menu() -> None:
    """Display the main menu."""
    print("\nStudent Database Menu")
    print("1. Display all students")
    print("2. Add a student")
    print("3. Update a student's email")
    print("4. Delete a student")
    print("5. Exit")


def main() -> None:
    """Run the interactive CRUD menu."""
    while True:
        print_menu()
        choice = input("Choose an option (1-5): ").strip()

        try:
            if choice == "1":
                getAllStudents()

            elif choice == "2":
                first_name = prompt_nonempty("First name: ")
                last_name = prompt_nonempty("Last name: ")
                email = prompt_nonempty("Email: ")
                enrollment_date = prompt_date("Enrollment date (YYYY-MM-DD): ")
                addStudent(first_name, last_name, email, enrollment_date)

            elif choice == "3":
                student_id = prompt_int("Student ID: ")
                new_email = prompt_nonempty("New email: ")
                updateStudentEmail(student_id, new_email)

            elif choice == "4":
                student_id = prompt_int("Student ID: ")
                deleteStudent(student_id)

            elif choice == "5":
                print("Exiting.")
                break

            else:
                print("Invalid option. Choose 1-5.")

        except errors.UniqueViolation:
            print("Error: that email address already exists. No changes were made.")
        except psycopg2.Error as exc:
            print(f"Database error: {exc}")
        except KeyboardInterrupt:
            print("\nInterrupted. Exiting.")
            sys.exit(1)


if __name__ == "__main__":
    main()