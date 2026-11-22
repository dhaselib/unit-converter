DEFAULT_EUR_RATES = {
    'USD': 1.1168,
    'GBP': 0.8349,
    'INR': 106.37,
    'CZK': 24.35,
    'DKK': 7.4736,
    'HUF': 365.55,
    'NOK': 10.35,
    'SEK': 11.00,
    'TRY': 55.78,
    'BRL': 6.01,
}
LIVE_EUR_RATES = DEFAULT_EUR_RATES.copy()
def convert_currency(to_u, from_u):
    if to_u == from_u:
        return 1.0, 0.0
    if to_u == 'EUR' and from_u == 'USDc':
        usd_rate = LIVE_EUR_RATES.get('USD', 1.1168)
        return 0.01 / usd_rate, 0.0
    if to_u == 'EUR' and from_u in LIVE_EUR_RATES:
        return 1.0 / LIVE_EUR_RATES[from_u], 0.0
    if from_u == 'EUR' and to_u in LIVE_EUR_RATES:
        return LIVE_EUR_RATES[to_u], 0.0
    if to_u in LIVE_EUR_RATES and from_u in LIVE_EUR_RATES:
        return LIVE_EUR_RATES[to_u] / LIVE_EUR_RATES[from_u], 0.0
    return None, None
