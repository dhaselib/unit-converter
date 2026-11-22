def convert_temp(to_u, from_u):
    temp_units = ['K', '°C', '°F', '°Ra', '°Re']
    if to_u in temp_units and from_u in temp_units:
        if from_u == 'K': fin, oin = 1.0, 0.0
        elif from_u == '°C': fin, oin = 1.0, 273.15
        elif from_u == '°F': fin, oin = 5.0 / 9.0, 255.37222222222223
        elif from_u == '°Ra': fin, oin = 5.0 / 9.0, 0.0
        elif from_u == '°Re': fin, oin = 1.25, 273.15
        else: fin, oin = 1.0, 0.0

        if to_u == 'K': fout, oout = 1.0, 0.0
        elif to_u == '°C': fout, oout = 1.0, -273.15
        elif to_u == '°F': fout, oout = 9.0 / 5.0, -459.67
        elif to_u == '°Ra': fout, oout = 9.0 / 5.0, 0.0
        elif to_u == '°Re': fout, oout = 0.8, -273.15 * 0.8
        else: fout, oout = 1.0, 0.0

        return fin * fout, oin * fout + oout
    return None, None
