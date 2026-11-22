TIME_FACTORS = {
    'ms': 0.001,
    's': 1.0,
    'min': 60.0,
    'h': 3600.0,
    'day': 86400.0,
    'week': 604800.0,
    'month': 2629746.0,
    'sem': 15778800.0,
    'year': 31556952.0,
}
def convert_time(to_u, from_u):
    if to_u in TIME_FACTORS and from_u in TIME_FACTORS:
        return TIME_FACTORS[from_u] / TIME_FACTORS[to_u], 0.0
    return None, None
