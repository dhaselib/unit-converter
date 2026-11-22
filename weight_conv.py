WEIGHT_FACTORS = {
    'u': 1.66053906660e-27,
    'mg': 1e-6,
    'cg': 1e-5,
    'dg': 1e-4,
    'g': 1e-3,
    'dag': 1e-2,
    'hg': 1e-1,
    'kg': 1.0,
    't': 1000.0,
    'Gg': 1e6,
    'Tg': 1e9,
    'oz': 0.028349523125,
    'lb': 0.45359237,
    'qr (UK)': 12.70058636,
    'qr (US)': 11.33980925,
    'slug': 14.5939029,
    'ton': 1016.0469088,
    'sh tn': 907.18474,
    'mol': 1.0,
    'lbmol': 453.59237,
}
def convert_weight(to_u, from_u):
    if to_u in WEIGHT_FACTORS and from_u in WEIGHT_FACTORS:
        return WEIGHT_FACTORS[from_u] / WEIGHT_FACTORS[to_u], 0.0
    return None, None
