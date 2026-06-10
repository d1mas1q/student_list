from datetime import datetime
import re


def validate_first_name_permissive(name: str) -> bool:
    # Clean the input by stripping trailing and leading spaces
    cleaned_name = name.strip()

    # Check length limits (e.g., minimum 1 character, maximum 50)
    if not (1 <= len(cleaned_name) <= 50):
        return False

    return True


def validate_last_name(last_name: str) -> bool:
    # Clean the input of accidental surrounding whitespace
    cleaned_name = last_name.strip()

    # Check length limits (Adjust max length based on database column constraints)
    if not (1 <= len(cleaned_name) <= 100):
        return False

    return True


def validate_groupnumber(text: str) -> bool:
    if not text or not isinstance(text, str):
        return False

    allowed = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
                  'абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
                  '0123456789')
    return all(c in allowed for c in text)

def validate_email(email: str) -> bool:
    return bool(email and '@' in email and '.' in email.split('@')[1])

def validate_examscore(exam_score):
    try:
        num = int(exam_score)
        return 0 <= num <= 400
    except (TypeError, ValueError):
        return False

def validate_birthyear(birth_year: int) -> bool:
    """Проверяет, что возраст от 16 до 80 лет"""
    try:
        current_year = datetime.now().year
        age = current_year - int(birth_year)
        return 16 <= age <= 100
    except (TypeError, ValueError):
        return False


def validate_student(student_data):
    errors = []

    if not validate_first_name_permissive(student_data['first_name']): errors.append('Некорректное имя')
    if not validate_last_name(student_data['last_name']): errors.append('Некорректная фамилия')
    if student_data['gender'] not in ("мужской", "женский"): errors.append('Некорректный пол')
    if not validate_groupnumber(student_data['group_number']) <= 5: errors.append('Некорректный номер группы')
    if not validate_email(student_data['email']): errors.append('Некорректный email')
    if not validate_examscore(student_data['exam_score']): errors.append('Некорректное значение баллов')
    if not validate_birthyear(student_data['birth_year']): errors.append('Некорректное значение года рождения')

    return errors