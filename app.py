from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from database import add_student, get_students, delete_student, update_student, get_student_by_id, StudentNotFoundError
from services.validator import validate_student
from jinja2 import Environment, FileSystemLoader

#Jinja2
env = Environment(loader=FileSystemLoader("templates"))

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

    def render_template(self, template_name, context):
        template = env.get_template(template_name)
        return template.render(**context)

    def get_value(self, params, key, default=''):
        return params.get(key, [default])[0]

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

    def show_students(self):
        students = get_students()
        html = self.render_template("list.html", {"students": students})
        self.send_html(html)

    def show_form(self):
        html = self.render_template('form.html', {})
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
        context = {'student' : student}
        html = self.render_template('edit.html', context)
        self.send_html(html)

    def create_student(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length).decode("utf-8")
        params = parse_qs(body)
        params = self.parse_student_form(params)
        errors = validate_student(params)

        if not errors:
            add_student(**params)
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
