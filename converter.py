CATEGORIES = {
    "length": "Longitud",
    "weight": "Peso",
    "temperature": "Temperatura",
}

# Factor de cada unidad respecto de la unidad base (metro para longitud, gramo para peso)
UNITS = {
    "length": {
        "mm": 0.001,
        "cm": 0.01,
        "m": 1,
        "km": 1000,
        "in": 0.0254,
        "ft": 0.3048,
        "yd": 0.9144,
        "mi": 1609.344,
    },
    "weight": {
        "mg": 0.001,
        "g": 1,
        "kg": 1000,
        "oz": 28.349523125,
        "lb": 453.59237,
    },
    # La temperatura no usa factores: se convierte con fórmulas
    "temperature": {"C": None, "F": None, "K": None},
}

# Nombre de cada unidad para mostrar en la página
UNIT_NAMES = {
    "mm": "Milímetro (mm)",
    "cm": "Centímetro (cm)",
    "m": "Metro (m)",
    "km": "Kilómetro (km)",
    "in": "Pulgada (in)",
    "ft": "Pie (ft)",
    "yd": "Yarda (yd)",
    "mi": "Milla (mi)",
    "mg": "Miligramo (mg)",
    "g": "Gramo (g)",
    "kg": "Kilogramo (kg)",
    "oz": "Onza (oz)",
    "lb": "Libra (lb)",
    "C": "Celsius (°C)",
    "F": "Fahrenheit (°F)",
    "K": "Kelvin (K)",
}


# Error por una conversión no válida
class ConversionError(Exception):
    pass


# Convierte pasando por la unidad base: primero a metros (o gramos) y luego a la unidad destino
def convert_by_factor(category, value, from_unit, to_unit):
    factors = UNITS[category]
    return value * factors[from_unit] / factors[to_unit]


# Temperatura mínima posible, en Celsius
ABSOLUTE_ZERO_C = -273.15


# Convierte cualquier escala a Celsius
def to_celsius(value, unit):
    if unit == "F":
        return (value - 32) * 5 / 9
    if unit == "K":
        return value - 273.15
    return value


# Convierte de Celsius a cualquier escala
def from_celsius(value, unit):
    if unit == "F":
        return value * 9 / 5 + 32
    if unit == "K":
        return value + 273.15
    return value


# Convierte pasando por Celsius; rechaza valores bajo el cero absoluto
def convert_temperature(value, from_unit, to_unit):
    celsius = to_celsius(value, from_unit)
    if celsius < ABSOLUTE_ZERO_C:
        raise ConversionError("La temperatura no puede ser menor que el cero absoluto (-273,15 °C).")
    return from_celsius(celsius, to_unit)
