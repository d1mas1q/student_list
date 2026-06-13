import sqlite3

from models.applicant import Student


class StudentNotFoundError(Exception):
    def __init__(self, student_id):
        super().__init__(
            f"Студент с id={student_id} не найден"
        )


def row_to_student(row):
    if not row:
        return None
    return Student(
        id=row['id'],
        first_name=row['first_name'],
        last_name=row['last_name'],
        gender=row['gender'],
        group_number=row['group_number'],
        email=row['email'],
        exam_score=row['exam_score'],
        birth_year=row['birth_year'],
        is_local=bool(row['is_local']),
        auth_token=row['auth_token']
    )


def execute(sql, params=()):
    with sqlite3.connect("test.db") as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute(sql, params)
        return cursor.rowcount

def fetch_one(sql, params=()):
    with sqlite3.connect("test.db") as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute(sql, params)
        return cursor.fetchone()

def fetch_all(sql, params=()):
    with sqlite3.connect("test.db") as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute(sql, params)
        return cursor.fetchall()

execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL CHECK(LENGTH(first_name) >= 2 AND LENGTH(first_name) <= 50),
            last_name TEXT NOT NULL CHECK(LENGTH(last_name) >= 2 AND LENGTH(last_name) <= 50),
            gender TEXT NOT NULL CHECK(gender IN ('мужской', 'женский')),
            group_number TEXT NOT NULL CHECK(LENGTH(group_number) BETWEEN 2 AND 5),
            email TEXT NOT NULL UNIQUE CHECK(email LIKE '%@%'),
            exam_score INTEGER NOT NULL CHECK(exam_score BETWEEN 0 AND 400),
            birth_year INTEGER NOT NULL,
            is_local BOOLEAN NOT NULL DEFAULT 1,
            auth_token TEXT UNIQUE
        )
    ''')


def add_student(first_name, last_name, gender, group_number, email, exam_score, birth_year, is_local, auth_token):
    sql = "INSERT INTO students (first_name, last_name, gender, group_number, email, exam_score, birth_year, is_local, auth_token) VALUES (?,?,?,?,?,?,?,?,?)"
    params = (first_name, last_name, gender, group_number, email, exam_score, birth_year, is_local, auth_token)
    execute(sql, params)



def get_students(sort='exam_score', order='desc'):
    sort = sort.lower() if sort else 'exam_score'
    order = order.lower() if order else 'desc'
    allowed_fields = ['first_name', 'last_name', 'group_number', 'exam_score']
    if sort not in allowed_fields:
        sort = 'exam_score'
    if order not in ['asc', 'desc']:
        order = 'desc'

    sql = f"SELECT * FROM students ORDER BY {sort} {order}"
    rows = fetch_all(sql)
    return [row_to_student(row) for row in rows]


def get_student_by_id(student_id):
    sql = "SELECT * FROM students WHERE id = ?"
    row = fetch_one(sql, (student_id,))
    if row is None: raise StudentNotFoundError(student_id)
    return row_to_student(row)

def get_student_by_token(auth_token):
    sql = "SELECT * FROM students WHERE auth_token = ?"
    row = fetch_one(sql, (auth_token,))
    return row_to_student(row)



def update_student(first_name, last_name, gender, group_number, email, exam_score, birth_year, is_local, student_id):
    sql = "UPDATE students SET first_name = ?, last_name = ?, gender = ?, group_number = ?, email = ?, exam_score = ?, birth_year = ?, is_local = ? WHERE id = ?"
    params = (first_name, last_name, gender, group_number, email, exam_score, birth_year, is_local, student_id)
    rows = execute(sql, params)
    if rows == 0: raise StudentNotFoundError(student_id)

def delete_student(student_id):
    sql = "DELETE FROM students WHERE id=?"
    params = (student_id,)
    rows = execute(sql, params)
    if rows == 0: raise StudentNotFoundError(student_id)

def find_students(query):
    search = '%' + query + '%'
    sql = "SELECT * FROM students WHERE LOWER(first_name) LIKE LOWER(?) or LOWER(last_name) LIKE LOWER(?) or LOWER(group_number) LIKE LOWER(?)"
    params = (search, search, search)
    rows = fetch_all(sql, params)
    return [row_to_student(row) for row in rows]