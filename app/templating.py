from fastapi.templating import Jinja2Templates
from fastapi import Request

# Указываем путь к папке с шаблонами относительно расположения этого файла
templates = Jinja2Templates(directory="/app/templates")

def render_template(request: Request, template_name: str, context: dict = None):
    if context is None:
        context = {}
    context.setdefault("request", request)
    return templates.TemplateResponse(template_name, context)