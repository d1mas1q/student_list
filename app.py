from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from database import add_student, get_students, delete_student, update_student
from services.validator import validate_student


class AppHandler(BaseHTTPRequestHandler):
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
                        """ for student in students)
        html = self.render_template("templates/list.html", {"students": res})
        self.send_html(html)

    def show_form(self):
        html = self.load_template("templates/form.html")
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
        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()

    def delete_student_view(self, student_id):
        delete_student(student_id)
        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()


    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        parts = parsed.path.strip('/').split("/")

        if parsed.path == "/":
            self.show_students()
        elif parsed.path == "/form":
            self.show_form()
        elif len(parts) == 3 and parts[0] == "students" and parts[2] == "delete":
            student_id = int(parts[1])
            self.delete_student_view(student_id)
        elif len(parts) == 3 and parts[0] == "students" and parts[2] == "edit":
            student_id = int(parts[1])
            first_name = params.get("first_name", [""])[0]
            email = params.get("email", [""])[0]
            update_student(first_name, email, student_id)

        else:
            html = "<h1>404 - Страница не найдена</h1>"
            self.send_html(html, status=404)

    def do_POST(self):
        if self.path == "/form":
            self.create_student()
        else:
            self.send_html(
                "<h1>404</h1>",
                status=404
            )


server = HTTPServer(("localhost", 8000), AppHandler)
print(f'serving at {server.server_address[0]}:{server.server_address[1]}')
server.serve_forever()
