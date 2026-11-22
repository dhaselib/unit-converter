import math
LENGTH_FACTORS = {
    'pm': 1e-12,
    'mm': 1e-3,
    'cm': 1e-2,
    'dm': 1e-1,
    'm': 1.0,
    'dam': 10.0,
    'hm': 100.0,
    'km': 1000.0,
    '100km': 100000.0,
    'in': 0.0254,
    'ft': 0.3048,
    'yd': 0.9144,
    'mi': 1609.344,
    'nmi': 1852.0,
}
def convert_length(to_u, from_u):
    if to_u in LENGTH_FACTORS and from_u in LENGTH_FACTORS:
        return LENGTH_FACTORS[from_u] / LENGTH_FACTORS[to_u], 0.0
    return None, None
