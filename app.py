import secrets
from http.cookies import SimpleCookie
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from database import add_student, get_students, delete_student, update_student, get_student_by_id, StudentNotFoundError, \
    get_student_by_token, find_students, get_students_count, find_students_count
from services.validator import validate_student
from services.templates import render_template
from settings import PER_PAGE, SUPERUSER_TOKEN


class AppHandler(BaseHTTPRequestHandler):

    def redirect(self, auth_token=None):
        self.send_response(302)
        if auth_token: self.send_header('Set-Cookie', f'auth_token={auth_token}; Max-Age=315360000')
        self.send_header("Location", "/")
        self.end_headers()


    def send_html(self, html, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))


    def get_post_params(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length).decode("utf-8")
        return parse_qs(body)


    def get_user_context(self):
        return {
            "current_token": self.get_auth_token(),
            "is_superuser": self.is_superuser(),
        }


    def get_auth_token(self):
        cookie_header = self.headers.get('Cookie')

        if not cookie_header:
            return None

        cookie = SimpleCookie()
        cookie.load(cookie_header)

        if 'auth_token' in cookie:
            return cookie['auth_token'].value

        return None


    def get_owned_student(self, student_id):
        try:
            student = get_student_by_id(student_id)
        except StudentNotFoundError:
            self.send_html(
                "<h1>404 - Студент не найден</h1>",
                status=404
            )
            return None

        if self.get_auth_token() == student.auth_token or self.is_superuser():
            return student

        self.send_html(
            "<h1>403 Forbidden</h1>",
            status=403
        )
        return None


    def admin_login(self):
        self.redirect(SUPERUSER_TOKEN)


    def logout(self):
        self.send_response(302)
        self.send_header('Set-Cookie', f'auth_token=; Max-Age=0')
        self.send_header("Location", "/")
        self.end_headers()


    def is_superuser(self):
        return self.get_auth_token() == SUPERUSER_TOKEN


    def get_value(self, params, key, default=''):
        return params.get(key, [default])[0]


    def get_page(self, params):
        try:
            page = int(self.get_value(params, 'page', '1'))
        except ValueError:
            page = 1
        if page < 1: page = 1
        return page


    def get_total_pages(self, total_students):
        return (total_students + PER_PAGE - 1) // PER_PAGE


    def parse_student_form(self, params):
        return {
            "first_name": self.get_value(params, "first_name"),
            "last_name": self.get_value(params, "last_name"),
            "gender": self.get_value(params, "gender"),
            "group_number": self.get_value(params, "group_number"),
            "email": self.get_value(params, "email"),
            "exam_score": self.get_value(params, "exam_score"),
            "birth_year": self.get_value(params, "birth_year"),
            "is_local": self.get_value(params, "is_local") == 'on',
        }


    def show_students(self, params):
        sort = self.get_value(params, 'sort', 'exam_score')
        order = self.get_value(params, 'order', 'desc')
        page = self.get_page(params)
        total_students = get_students_count()
        total_pages = self.get_total_pages(total_students)
        students = get_students(sort, order, page)

        html = render_template(
            "list.html",
            {
                **self.get_user_context(),
                "students": students,
                "page": page,
                "total_pages": total_pages,
                "sort": sort,
                "order": order
            }
        )
        self.send_html(html)


    def show_form(self):
        auth_token = self.get_auth_token()

        if auth_token and get_student_by_token(auth_token):
            self.redirect()
            return

        html = render_template(
            "form.html",
            {
                "student": {},
                "errors": {}
            }
        )
        self.send_html(html)


    def show_edit_form(self, student_id):
        student = self.get_owned_student(student_id)
        if student:
            html = render_template('edit.html', {'student': student, 'errors': {}})
            self.send_html(html)


    def show_admin_login(self, error=''):
        if self.is_superuser():
            self.redirect()
            return
        html = render_template('admin-login.html', {'error': error})
        self.send_html(html)


    def show_search(self, params):
        query = self.get_value(params, 'q')
        print(params)
        page = self.get_page(params)
        sort = self.get_value(params, 'sort', 'exam_score')
        order = self.get_value(params, 'order', 'desc')

        if query:
            total_students = find_students_count(query)
            students = find_students(query, sort, order, page)
            total_pages = self.get_total_pages(total_students)
        else:
            students = []
            total_pages = 0
        html = render_template(
            "search.html",
            {
                **self.get_user_context(),
                "query": query,
                "page": page,
                "students": students,
                "total_pages": total_pages,
                "sort": sort,
                "order": order
            }
        )
        self.send_html(html)


    def create_student(self):
        params = self.get_post_params()
        student = self.parse_student_form(params)
        errors = validate_student(student)

        if not errors:
            student['auth_token'] = secrets.token_hex(16)
            add_student(**student)
            self.redirect(student['auth_token'])
        else:
            html = render_template(
                "form.html",
                {
                    "errors": errors,
                    "student": student
                }
            )
            self.send_html(html)
            return


    def delete_student_view(self, student_id):
        student = self.get_owned_student(student_id)

        if not student:
            return

        delete_student(student_id)
        self.redirect()


    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        parts = parsed.path.strip('/').split("/")

        if parsed.path == "/":
            self.show_students(params)
        elif parsed.path == "/form":
            self.show_form()
        elif parsed.path == '/search':
            self.show_search(params)
        elif parsed.path == '/admin-login':
            self.show_admin_login()
        elif parsed.path == '/logout':
            self.logout()
        elif len(parts) == 3 and parts[0] == "students" and parts[2] == "delete":
            self.delete_student_view(int(parts[1]))
        elif len(parts) == 3 and parts[0] == "students" and parts[2] == "edit":
            self.show_edit_form(int(parts[1]))

        else:
            html = "<h1>404 - Страница не найдена</h1>"
            self.send_html(html, status=404)

    def do_POST(self):
        parsed = urlparse(self.path)
        parts = parsed.path.strip('/').split("/")

        if self.path == "/form":
            self.create_student()
        elif parsed.path == '/admin-login':
            params = self.get_post_params()
            token = self.get_value(params, 'token')
            if token == SUPERUSER_TOKEN: self.admin_login()
            else:
                self.show_admin_login('Неверный токен')
                return 
        elif len(parts) == 3 and parts[0] == "students" and parts[2] == "edit":
            params = self.get_post_params()
            student = self.parse_student_form(params)
            errors = validate_student(student)
            if errors:
                html = render_template('edit.html', {'student': student, 'errors': errors})
                self.send_html(html)
                return

            student_db = self.get_owned_student(int(parts[1]))
            if not student_db:
                return

            update_student(**student, student_id=int(parts[1]))
            self.redirect()
        else:
            self.send_html(
                "<h1>404</h1>",
                status=404
            )


server = HTTPServer(("0.0.0.0", 8000), AppHandler)
print(f'serving at {server.server_address[0]}:{server.server_address[1]}')
server.serve_forever()