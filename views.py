import html
from pathlib import Path
from string import Template

import converter

# Ruta de la plantilla relativa a este archivo, no a la carpeta desde donde se ejecuta
TEMPLATE_PATH = Path(__file__).parent / "templates" / "base.html"
BASE_TEMPLATE = Template(TEMPLATE_PATH.read_text(encoding="utf-8"))


# Pestañas de navegación; la de la categoría actual queda marcada
def render_tabs(active_category):
    links = []
    for category, name in converter.CATEGORIES.items():
        css_class = ' class="active"' if category == active_category else ""
        links.append(f'<a href="/{category}"{css_class}>{name}</a>')
    return "\n".join(links)


# Página completa; la plantilla base con las pestañas y el contenido
def render_page(category, content):
    title = converter.CATEGORIES.get(category, "Página no encontrada")
    return BASE_TEMPLATE.substitute(title=title, tabs=render_tabs(category), content=content)


# Opciones de un <select>; queda marcada la unidad elegida
def render_unit_options(category, selected):
    options = []
    for unit in converter.UNITS[category]:
        selected_attr = " selected" if unit == selected else ""
        options.append(f'<option value="{unit}"{selected_attr}>{converter.UNIT_NAMES[unit]}</option>')
    return "\n".join(options)


# Formulario de conversión; conserva lo ingresado y muestra el error, si lo hay
def render_form(category, values=None, error=None):
    values = values or {}
    units = list(converter.UNITS[category])

    # Todo lo que viene del usuario se escapa antes de ponerlo en el HTML
    value = html.escape(values.get("value", ""))
    error_html = f'<p class="error">{html.escape(error)}</p>' if error else ""

    # Por defecto convierte de la primera unidad a la segunda
    from_unit = values.get("from_unit", units[0])
    to_unit = values.get("to_unit", units[1])

    content = f"""
    {error_html}
    <form method="post">
      <label for="value">Valor a convertir</label>
      <input id="value" name="value" value="{value}" required autofocus>

      <label for="from_unit">Convertir desde</label>
      <select id="from_unit" name="from_unit">{render_unit_options(category, from_unit)}</select>

      <label for="to_unit">Convertir a</label>
      <select id="to_unit" name="to_unit">{render_unit_options(category, to_unit)}</select>

      <button class="button" type="submit">Convertir</button>
    </form>"""
    return render_page(category, content)


# Símbolo para mostrar en el resultado
def unit_symbol(unit):
    return f"°{unit}" if unit in ("C", "F") else unit


# Resultado de la conversión con el botón para volver al formulario
def render_result(category, value, from_unit, to_unit, result):
    content = f"""
    <p>Resultado de tu conversión</p>
    <p class="result">{converter.format_number(value)} {unit_symbol(from_unit)} = {converter.format_number(result)} {unit_symbol(to_unit)}</p>
    <a class="button" href="/{category}">Reiniciar</a>"""
    return render_page(category, content)


# Página para rutas que no existen
def render_not_found():
    content = """
    <p>La página que buscas no existe.</p>
    <a class="button" href="/length">Ir al conversor</a>"""
    return render_page(None, content)
