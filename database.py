import sqlite3
from models.applicant import Student


class StudentNotFoundError(Exception):
    def __init__(self, student_id):
        super().__init__(
            f"Студент с id={student_id} не найден"
        )



def execute(sql, params=()):
    with sqlite3.connect("test.db") as connection:
        cursor = connection.cursor()
        cursor.execute(sql, params)
        return cursor.rowcount

def fetch_one(sql, params=()):
    with sqlite3.connect("test.db") as connection:
        cursor = connection.cursor()
        cursor.execute(sql, params)
        return cursor.fetchone()

def fetch_all(sql, params=()):
    with sqlite3.connect("test.db") as connection:
        cursor = connection.cursor()
        cursor.execute(sql, params)
        return cursor.fetchall()

execute('''CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    email TEXT NOT NULL
);''')


def add_student(first_name, email):
    sql = "INSERT INTO students (first_name, email) VALUES (?,?)"
    params = (first_name, email)
    execute(sql, params)



def get_students():
    sql = "SELECT id, first_name, email FROM students"
    rows = fetch_all(sql)
    return [Student(*row) for row in rows]


def get_student_by_id(student_id):
    sql = "SELECT id, first_name, email FROM students WHERE id = ?"
    row = fetch_one(sql, (student_id,))
    if row is None: raise StudentNotFoundError(student_id)
    return Student(*row)


def update_student(first_name, email, student_id):
    sql = "UPDATE students SET first_name = ?, email = ? WHERE id = ?"
    params = (first_name, email, student_id)
    rows = execute(sql, params)
    if rows == 0: raise StudentNotFoundError(student_id)

def delete_student(student_id):
    sql = "DELETE FROM students WHERE id=?"
    params = (student_id,)
    rows = execute(sql, params)
    if rows == 0: raise StudentNotFoundError(student_id)