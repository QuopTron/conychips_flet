"""
🔄 Conversiones de Unidades de Medida
Sistema local para convertir entre unidades comunes sin depender de API externa
"""

# Diccionario de conversiones: {unidad_origen: {unidad_destino: factor}}
CONVERSIONES = {
    # PESO (base: gramos)
    "gr": {"gr": 1, "kg": 0.001, "lb": 0.00220462, "arroba": 0.0000625, "oz": 0.035274},
    "kg": {"gr": 1000, "kg": 1, "lb": 2.20462, "arroba": 0.0625, "oz": 35.274},
    "lb": {"gr": 453.592, "kg": 0.453592, "lb": 1, "arroba": 0.0284091, "oz": 16},
    "arroba": {"gr": 16000, "kg": 16, "lb": 35.2739, "arroba": 1, "oz": 564.384},
    "oz": {"gr": 28.3495, "kg": 0.0283495, "lb": 0.0625, "arroba": 0.0017716, "oz": 1},
    
    # VOLUMEN (base: litros)
    "litro": {"litro": 1, "ml": 1000, "gallon": 0.264172, "taza": 4.22675, "onza_fl": 33.814},
    "ml": {"litro": 0.001, "ml": 1, "gallon": 0.000264172, "taza": 0.00422675, "onza_fl": 0.033814},
    "gallon": {"litro": 3.78541, "ml": 3785.41, "gallon": 1, "taza": 16, "onza_fl": 128},
    "taza": {"litro": 0.236588, "ml": 236.588, "gallon": 0.0625, "taza": 1, "onza_fl": 8},
    "onza_fl": {"litro": 0.0295735, "ml": 29.5735, "gallon": 0.0078125, "taza": 0.125, "onza_fl": 1},
    
    # LONGITUD (base: cm)
    "cm": {"cm": 1, "m": 0.01, "km": 0.00001, "in": 0.393701, "ft": 0.0328084},
    "m": {"cm": 100, "m": 1, "km": 0.001, "in": 39.3701, "ft": 3.28084},
    "km": {"cm": 100000, "m": 1000, "km": 1, "in": 39370.1, "ft": 3280.84},
    "in": {"cm": 2.54, "m": 0.0254, "km": 0.0000254, "in": 1, "ft": 0.0833333},
    "ft": {"cm": 30.48, "m": 0.3048, "km": 0.0003048, "in": 12, "ft": 1},
}

# Sinónimos de unidades para flexibilidad
SINONIMOS = {
    # Peso
    "gramo": "gr",
    "gramos": "gr",
    "kilogramo": "kg",
    "kilogramos": "kg",
    "kilo": "kg",
    "kilos": "kg",
    "libra": "lb",
    "libras": "lb",
    "arroba": "arroba",
    "arrobas": "arroba",
    "onza": "oz",
    "onzas": "oz",
    
    # Volumen
    "litros": "litro",
    "l": "litro",
    "mililitro": "ml",
    "mililitros": "ml",
    "galón": "gallon",
    "galones": "gallon",
    "tazas": "taza",
    "onza_fluida": "onza_fl",
    "onzas_fluidas": "onza_fl",
    "fl_oz": "onza_fl",
    
    # Longitud
    "centímetro": "cm",
    "centímetros": "cm",
    "metro": "m",
    "metros": "m",
    "kilómetro": "km",
    "kilómetros": "km",
    "pulgada": "in",
    "pulgadas": "in",
    "pie": "ft",
    "pies": "ft",
    "foot": "ft",
    "feet": "ft",
    "inch": "in",
    "inches": "in",
}


def normalizar_unidad(unidad: str) -> str:
    """Normaliza el nombre de la unidad a su forma estándar"""
    unidad_norm = unidad.strip().lower()
    
    # Si es sinónimo, devolver la unidad estándar
    if unidad_norm in SINONIMOS:
        return SINONIMOS[unidad_norm]
    
    # Si es una unidad estándar, devolverla
    if unidad_norm in CONVERSIONES:
        return unidad_norm
    
    return None


def convertir(cantidad: float, de_unidad: str, a_unidad: str) -> float | None:
    """
    Convierte una cantidad de una unidad a otra
    
    Args:
        cantidad: Cantidad a convertir
        de_unidad: Unidad origen (ej: "kg", "lb", "litro")
        a_unidad: Unidad destino (ej: "gr", "oz", "ml")
    
    Returns:
        Cantidad convertida, o None si las unidades no son válidas
    
    Ejemplo:
        convertir(1, "kg", "gr")  # 1000
        convertir(2, "lb", "kg")  # 0.907184
    """
    # Normalizar unidades
    de = normalizar_unidad(de_unidad)
    a = normalizar_unidad(a_unidad)
    
    if not de or not a:
        return None
    
    # Si son la misma unidad, retornar cantidad sin cambios
    if de == a:
        return cantidad
    
    # Verificar si la conversión es posible
    if de not in CONVERSIONES or a not in CONVERSIONES[de]:
        return None
    
    # Realizar conversión
    factor = CONVERSIONES[de][a]
    return cantidad * factor


def obtener_unidades_compatibles(unidad: str) -> list[str]:
    """
    Retorna lista de unidades a las que se puede convertir
    
    Ejemplo:
        obtener_unidades_compatibles("kg")  # ["gr", "kg", "lb", "arroba", "oz"]
    """
    unidad_norm = normalizar_unidad(unidad)
    if not unidad_norm or unidad_norm not in CONVERSIONES:
        return []
    
    return list(CONVERSIONES[unidad_norm].keys())


def es_unidad_peso(unidad: str) -> bool:
    """Verifica si una unidad es de peso"""
    norm = normalizar_unidad(unidad)
    unidades_peso = {"gr", "kg", "lb", "arroba", "oz"}
    return norm in unidades_peso


def es_unidad_volumen(unidad: str) -> bool:
    """Verifica si una unidad es de volumen"""
    norm = normalizar_unidad(unidad)
    unidades_volumen = {"litro", "ml", "gallon", "taza", "onza_fl"}
    return norm in unidades_volumen


def es_unidad_longitud(unidad: str) -> bool:
    """Verifica si una unidad es de longitud"""
    norm = normalizar_unidad(unidad)
    unidades_longitud = {"cm", "m", "km", "in", "ft"}
    return norm in unidades_longitud


def obtener_categorias() -> list:
    """Retorna las categorías disponibles de unidades"""
    return ["PESO", "VOLUMEN", "LONGITUD"]


def obtener_unidades_por_categoria(categoria: str) -> list:
    """Retorna lista de unidades para una categoría"""
    if categoria == "PESO":
        return ["gr", "kg", "lb", "oz", "arroba"]
    elif categoria == "VOLUMEN":
        return ["ml", "litro", "gallon", "taza", "onza_fl"]
    elif categoria == "LONGITUD":
        return ["cm", "m", "km", "in", "ft"]
    return []


def obtener_categoria_unidad(unidad: str) -> str:
    """Retorna la categoría de una unidad"""
    norm = normalizar_unidad(unidad)
    if es_unidad_peso(norm):
        return "PESO"
    elif es_unidad_volumen(norm):
        return "VOLUMEN"
    elif es_unidad_longitud(norm):
        return "LONGITUD"
    return "DESCONOCIDA"


# Para testing y referencia
if __name__ == "__main__":
    # Ejemplos de uso
    print("=== Ejemplos de conversiones ===")
    print(f"1 kg = {convertir(1, 'kg', 'gr')} gr")
    print(f"2 lb = {convertir(2, 'lb', 'kg')} kg")
    print(f"500 ml = {convertir(500, 'ml', 'litro')} litros")
    print(f"30 gr = {convertir(30, 'gr', 'oz')} oz")
    print()
    print("=== Unidades compatibles ===")
    print(f"kg → {obtener_unidades_compatibles('kg')}")
    print(f"litro → {obtener_unidades_compatibles('litro')}")
    print()
    print("=== Validaciones ===")
    print(f"¿kg es peso? {es_unidad_peso('kg')}")
    print(f"¿ml es volumen? {es_unidad_volumen('ml')}")
    print(f"¿m es longitud? {es_unidad_longitud('m')}")
