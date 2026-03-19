import jinja2
import os

template_dir = r"c:\Users\victo\OneDrive\Desktop\Proyectos\CLUBDEROBOTICA - App\ClubDeRobotica\app\templates"
loader = jinja2.FileSystemLoader(template_dir)
env = jinja2.Environment(loader=loader)

try:
    env.get_template('miembros/index.html')
    print("Template parsed successfully.")
except jinja2.TemplateSyntaxError as e:
    print(f"TemplateSyntaxError: {e}")
    print(f"File: {e.filename}")
    print(f"Line: {e.lineno}")
except Exception as e:
    print(f"Error: {e}")
