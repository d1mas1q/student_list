from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from database import add_student, get_students, delete_student, update_student, get_student_by_id, StudentNotFoundError
from services.validator import validate_student


class AppHandler(BaseHTTPRequestHandler):

    def redirect(self):
        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()

    def send_html(self, html, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def load_template(self, path):
        with open(path, encoding="utf-8") as file:
            return file.read()

    def render_template(self, path, context):
        with open(path, encoding="utf-8") as file:
            html = file.read()

        for key, value in context.items():
            html = html.replace(
                "{{ " + key + " }}",
                str(value)
            )

        return html

    def show_students(self):
        students = get_students()
        res = "".join(f"""
                        <p>
                            Name: {student.first_name},
                            Email: {student.email}
                        </p>
                        <a href="/students/{student.id}/delete">
                            Удалить
                        </a>
                        <a href="/students/{student.id}/edit">
                            Изменить
                        </a>
                        """ for student in students)
        html = self.render_template("templates/list.html", {"students": res})
        self.send_html(html)

    def show_form(self):
        html = self.load_template("templates/form.html")
        self.send_html(html)

    def show_edit_form(self, student_id):
        try:
            student = get_student_by_id(student_id)
        except StudentNotFoundError:
            self.send_html(
                "<h1>404 - Студент не найден</h1>",
                status=404
            )
            return
        context = {'id': student_id,
                   'first_name': student.first_name,
                   'email': student.email}
        html = self.render_template('templates/edit.html', context)
        self.send_html(html)

    def create_student(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length).decode("utf-8")
        params = parse_qs(body)
        first_name = params.get("first_name", [""])[0]
        email = params.get("email", [""])[0]
        errors = validate_student(first_name, email)

        if not errors:
            add_student(first_name, email)
        self.redirect()

    def delete_student_view(self, student_id):
        delete_student(student_id)
        self.redirect()


    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        parts = parsed.path.strip('/').split("/")

        if parsed.path == "/":
            self.show_students()
        elif parsed.path == "/form":
            self.show_form()
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
        elif len(parts) == 3 and parts[0] == "students" and parts[2] == "edit":
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length).decode("utf-8")
            params = parse_qs(body)
            first_name = params.get("first_name", [""])[0]
            email = params.get("email", [""])[0]
            update_student(first_name, email, int(parts[1]))
            self.redirect()
        else:
            self.send_html(
                "<h1>404</h1>",
                status=404
            )


server = HTTPServer(("localhost", 8000), AppHandler)
print(f'serving at {server.server_address[0]}:{server.server_address[1]}')
server.serve_forever()
