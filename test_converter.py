import unittest

import converter
import views


class TestConvert(unittest.TestCase):
    # Conversiones conocidas de longitud y peso
    def test_length_and_weight(self):
        self.assertAlmostEqual(converter.convert("length", 20, "ft", "cm"), 609.6)
        self.assertAlmostEqual(converter.convert("length", 1, "mi", "km"), 1.609344)
        self.assertAlmostEqual(converter.convert("weight", 1, "lb", "g"), 453.59237)
        self.assertAlmostEqual(converter.convert("weight", 1500, "mg", "g"), 1.5)

    # Conversiones conocidas de temperatura
    def test_temperature(self):
        self.assertAlmostEqual(converter.convert("temperature", 0, "C", "F"), 32)
        self.assertAlmostEqual(converter.convert("temperature", 100, "C", "K"), 373.15)
        self.assertAlmostEqual(converter.convert("temperature", -40, "F", "C"), -40)

    # Rechaza temperaturas bajo el cero absoluto
    def test_below_absolute_zero(self):
        with self.assertRaises(converter.ConversionError):
            converter.convert("temperature", -300, "C", "F")
        with self.assertRaises(converter.ConversionError):
            converter.convert("temperature", -1, "K", "C")

    # Rechaza categorías y unidades que no existen o que no son de la categoría
    def test_invalid_units(self):
        for category, from_unit, to_unit in [("volume", "l", "ml"), ("length", "ft", "kg"), ("weight", None, "g")]:
            with self.subTest(category=category, from_unit=from_unit, to_unit=to_unit):
                with self.assertRaises(converter.ConversionError):
                    converter.convert(category, 1, from_unit, to_unit)


class TestParseAndFormat(unittest.TestCase):
    # Acepta punto o coma decimal y espacios alrededor
    def test_parse_value(self):
        self.assertEqual(converter.parse_value("20"), 20)
        self.assertEqual(converter.parse_value(" 1,5 "), 1.5)
        self.assertEqual(converter.parse_value("-3.25"), -3.25)

    # Rechaza texto vacío, texto no numérico, nan e inf
    def test_parse_value_rejects_invalid_input(self):
        for text in ["", "abc", "nan", "inf", "1,000.5"]:
            with self.subTest(text=text):
                with self.assertRaises(converter.ConversionError):
                    converter.parse_value(text)

    # Hasta 4 decimales sin ceros finales; los valores muy pequeños, en notación científica
    def test_format_number(self):
        self.assertEqual(converter.format_number(609.6), "609.6")
        self.assertEqual(converter.format_number(1.1 * 3), "3.3")
        self.assertEqual(converter.format_number(32.0), "32")
        self.assertEqual(converter.format_number(0.000006214), "6.214e-06")


class TestViews(unittest.TestCase):
    # El texto del usuario se escapa: el navegador lo muestra, no lo ejecuta
    def test_form_escapes_user_input(self):
        page = views.render_form("length", {"value": "<script>alert(1)</script>"}, "Error")

        self.assertNotIn("<script>", page)
        self.assertIn("&lt;script&gt;", page)

    # El formulario conserva las unidades elegidas
    def test_form_keeps_selected_units(self):
        page = views.render_form("length", {"value": "20", "from_unit": "ft", "to_unit": "cm"})

        self.assertIn('value="ft" selected', page)
        self.assertIn('value="cm" selected', page)

    # El resultado muestra los grados con su símbolo
    def test_result_shows_conversion(self):
        page = views.render_result("temperature", 100, "C", "F", 212.0)

        self.assertIn("100 °C = 212 °F", page)