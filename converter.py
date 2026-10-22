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
