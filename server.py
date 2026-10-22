from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

import converter
import views

# Solo acepta conexiones desde este mismo computador
HOST = "127.0.0.1"
PORT = 8000

# Tamaño máximo aceptado para el formulario, en bytes
MAX_BODY_SIZE = 1024


class ConverterHandler(BaseHTTPRequestHandler):
    # Envía una página HTML con el código de estado indicado
    def send_html(self, status, page):
        body = page.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # Categoría de la ruta pedida (/length -> "length"), o None si no existe
    def get_category(self):
        # urlsplit separa la ruta de los parámetros: /length?x=1 -> /length
        name = urlsplit(self.path).path.strip("/")
        return name if name in converter.CATEGORIES else None

    def do_GET(self):
        # La raíz redirige a la primera pestaña
        if urlsplit(self.path).path == "/":
            self.send_response(HTTPStatus.FOUND)
            self.send_header("Location", "/length")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return

        category = self.get_category()
        if category is None:
            self.send_html(HTTPStatus.NOT_FOUND, views.render_not_found())
            return

        self.send_html(HTTPStatus.OK, views.render_form(category))

    # Lee el cuerpo del POST y devuelve los campos del formulario como diccionario
    def read_form(self, length):
        body = self.rfile.read(length).decode("utf-8", errors="replace")
        # Se toma el primer valor de cada campo
        return {name: values[0] for name, values in parse_qs(body).items()}

    def do_POST(self):
        category = self.get_category()
        if category is None:
            self.send_html(HTTPStatus.NOT_FOUND, views.render_not_found())
            return

        # El navegador indica el tamaño del formulario; se rechaza si falta o es demasiado grande
        try:
            length = int(self.headers.get("Content-Length", ""))
        except ValueError:
            self.send_error(HTTPStatus.LENGTH_REQUIRED)
            return
        if length < 0 or length > MAX_BODY_SIZE:
            self.send_error(HTTPStatus.REQUEST_ENTITY_TOO_LARGE)
            return

        form = self.read_form(length)
        try:
            value = converter.parse_value(form.get("value", ""))
            result = converter.convert(category, value, form.get("from_unit"), form.get("to_unit"))
        except converter.ConversionError as error:
            # Vuelve a mostrar el formulario con lo ingresado y el mensaje de error
            self.send_html(HTTPStatus.BAD_REQUEST, views.render_form(category, form, str(error)))
            return

        page = views.render_result(category, value, form["from_unit"], form["to_unit"], result)
        self.send_html(HTTPStatus.OK, page)


def main():
    server = ThreadingHTTPServer((HOST, PORT), ConverterHandler)
    print(f"Servidor en http://{HOST}:{PORT} (Ctrl+C para detener)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        # Libera el puerto aunque ocurra un error
        server.server_close()


if __name__ == "__main__":
    main()
