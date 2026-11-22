VOLUME_FACTORS = {
    'mm3': 1e-9,
    'cm3': 1e-6,
    'ml': 1e-6,
    'dm3': 1e-3,
    'l': 1e-3,
    'm3': 1.0,
    'fl oz (UK)': 2.84130625e-5,
    'fl oz (US)': 2.95735295625e-5,
    'pt (UK)': 0.00056826125,
    'liq pt': 0.000473176473,
    'dry pt': 0.0005506104713575,
    'qt (UK)': 0.0011365225,
    'liq qt': 0.000946352946,
    'dry qt': 0.001101220942715,
    'gal (UK)': 0.00454609,
    'gal (US)': 0.003785411784,
    'dry gal': 0.00440488377086,
    'bbl': 0.158987294928,
    'in3': 1.6387064e-5,
    'ft3': 0.028316846592,
    'yd3': 0.764554857984,
    'FBM': 0.002359737216,
}
def convert_volume(to_u, from_u):
    if to_u in VOLUME_FACTORS and from_u in VOLUME_FACTORS:
        return VOLUME_FACTORS[from_u] / VOLUME_FACTORS[to_u], 0.0
    return None, None
