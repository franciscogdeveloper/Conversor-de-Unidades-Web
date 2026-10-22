import http.client
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.parse import urlencode

import server


# Handler que no escribe el log de cada petición, para no ensuciar la salida de los tests
class QuietHandler(server.ConverterHandler):
    def log_message(self, format, *args):
        pass


class TestServer(unittest.TestCase):
    # Levanta el servidor real una sola vez para todos los tests, en un puerto libre
    @classmethod
    def setUpClass(cls):
        # Puerto 0: el sistema operativo elige uno libre
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), QuietHandler)
        cls.port = cls.httpd.server_address[1]
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    # Detiene el servidor al terminar todos los tests
    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.thread.join()

    # Hace una petición y devuelve el código, las cabeceras y el cuerpo
    def request(self, method, path, form=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        body = urlencode(form) if form is not None else None
        headers = {"Content-Type": "application/x-www-form-urlencoded"} if form is not None else {}
        connection.request(method, path, body=body, headers=headers)
        response = connection.getresponse()
        content = response.read().decode("utf-8")
        connection.close()
        return response.status, response.headers, content

    # La raíz redirige a la página de longitud
    def test_root_redirects_to_length(self):
        status, headers, _ = self.request("GET", "/")

        self.assertEqual(status, 302)
        self.assertEqual(headers["Location"], "/length")

    # Cada categoría muestra su formulario
    def test_get_category_pages(self):
        for path in ["/length", "/weight", "/temperature"]:
            with self.subTest(path=path):
                status, headers, content = self.request("GET", path)
                self.assertEqual(status, 200)
                self.assertIn("text/html", headers["Content-Type"])
                self.assertIn('<form method="post">', content)

    # Una ruta que no existe responde 404
    def test_unknown_path_returns_404(self):
        status, _, content = self.request("GET", "/nada")

        self.assertEqual(status, 404)
        self.assertIn("no existe", content)

    # Un formulario válido devuelve el resultado
    def test_post_valid_form(self):
        status, _, content = self.request("POST", "/length", {"value": "20", "from_unit": "ft", "to_unit": "cm"})

        self.assertEqual(status, 200)
        self.assertIn("20 ft = 609.6 cm", content)

    # Un formulario inválido devuelve 400 con el error y lo ingresado
    def test_post_invalid_form(self):
        status, _, content = self.request("POST", "/temperature", {"value": "-300", "from_unit": "C", "to_unit": "F"})

        self.assertEqual(status, 400)
        self.assertIn("cero absoluto", content)
        self.assertIn('value="-300"', content)

    # Un formulario demasiado grande se rechaza sin procesarlo
    def test_post_too_large(self):
        status, _, _ = self.request("POST", "/length", {"value": "1" * 2000})

        self.assertEqual(status, 413)
