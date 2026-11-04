# Student Database App

A Python application that connects to PostgreSQL and performs CRUD operations on a `students` table.

> **Assumptions:** Python 3.9+, `pip`, `git`, and PostgreSQL are already installed and the PostgreSQL service is running. This README targets Pop!_OS / Ubuntu / Debian.

## Demonstration Video

[Youtube Video Demo](https://www.youtube.com/watch?v=CaKEC3WLEO8)

## Functions

- `getAllStudents()`: Retrieves and displays all student records.
- `addStudent(first_name, last_name, email, enrollment_date)`: Inserts a new student.
- `updateStudentEmail(student_id, new_email)`: Updates the email of a student.
- `deleteStudent(student_id)`: Deletes a student record.

## Project Structure

```text
student-db-app/
├── database/
│   └── schema.sql
├── app/
│   └── main.py
├── requirements.txt
└── README.md
```

---

## 1 - Create the application database and user

```bash
sudo -u postgres psql -c "CREATE USER student_user WITH PASSWORD 'student_pass';"
sudo -u postgres psql -c "CREATE DATABASE student_db OWNER student_user;"
```

Verify password auth over TCP (the app connects this way):

```bash
PGPASSWORD=student_pass psql -h localhost -p 5432 -U student_user -d student_db -c "SELECT current_user, current_database();"
```

Expected: `student_user | student_db`.

## 2 - Clone the repository

```bash
git clone https://github.com/YESSIE-88/student-db-app
cd student-db-app
```

## 3 - Load the schema and initial data

```bash
PGPASSWORD=student_pass psql -h localhost -p 5432 -U student_user -d student_db -f database/schema.sql
```

Verify the three seeded rows:

```bash
PGPASSWORD=student_pass psql -h localhost -p 5432 -U student_user -d student_db -c "SELECT * FROM students ORDER BY student_id;"
```

## 4 - Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 5 - Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 6 - Set the database connection environment variables

```bash
export PGHOST=localhost
export PGPORT=5432
export PGDATABASE=student_db
export PGUSER=student_user
export PGPASSWORD=student_pass
```

> These apply only to the current shell. Re-run this block in each new terminal, or add it to `~/.bashrc`.

## 7 - Run the application

```bash
python app/main.py
```

```text
Student Database Menu
1. Display all students
2. Add a student
3. Update a student's email
4. Delete a student
5. Exit
Choose an option (1-5):
```