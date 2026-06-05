import sqlite3
from models.applicant import Student


connection = sqlite3.connect('test.db')
cursor = connection.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    email TEXT NOT NULL
);''')
connection.commit()
connection.close()


class StudentNotFoundError(Exception):
    pass


def add_student(first_name, email):
    connection = sqlite3.connect('test.db')
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO students (first_name, email) VALUES (?,?)",
        (first_name, email)
    )
    connection.commit()
    connection.close()


def get_students():
    connection = sqlite3.connect('test.db')
    cursor = connection.cursor()
    cursor.execute("SELECT id, first_name, email FROM students")
    rows = cursor.fetchall()
    connection.close()
    return [Student(*row) for row in rows]


def get_student_by_id(student_id):
    connection = sqlite3.connect("test.db")
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id, first_name, email FROM students WHERE id = ?",
        (student_id,)
    )

    row = cursor.fetchone()
    connection.close()

    if row is None:
        raise StudentNotFoundError(
            f"Student with id={student_id} not found"
        )

    return Student(*row)


def update_student(first_name, email, id):
    connection = sqlite3.connect('test.db')
    cursor = connection.cursor()
    cursor.execute("UPDATE students SET first_name = ?, email = ? WHERE id = ?", (first_name, email, id))
    connection.commit()
    connection.close()

def delete_student(student_id):
    connection = sqlite3.connect('test.db')
    cursor = connection.cursor()
    cursor.execute("DELETE FROM students WHERE id=?", (student_id,))
    connection.commit()
    connection.close()