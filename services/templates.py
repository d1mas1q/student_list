from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader("templates"))

def render_template(template_name, context):
    template = env.get_template(template_name)
    return template.render(**context)