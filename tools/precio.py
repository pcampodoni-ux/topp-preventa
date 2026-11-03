# Fórmula TOPP: (USD x 1,07 + flete_por_prenda_USD) x cotización x margen
# redondeo a la centena - 10; terminaciones 090/190/290/390/490 -> 990
FLETE_PRENDA_USD = 6.94   # = peso_kg x flete_USD_kg (calibrado con pedidos de junio)
MARGEN = 1.9
UMBRAL_PSICO = 3000  # $70.000–$72.990 -> $69.900
def precio(usd, cot, flete=None):
    raw = (usd*1.07 + (FLETE_PRENDA_USD if flete is None else flete)) * cot * MARGEN
    r = int(round(raw/100.0))*100 - 10
    m = r % 1000
    if m in (90,190,290,390,490): r = r - m + 990
    # precio psicológico: si pasa apenas una decena de mil (hasta $2.990 arriba), baja a X9.900
    if r >= 10000 and r % 10000 < UMBRAL_PSICO:
        r = (r // 10000) * 10000 - 100
    return r
def precio_sin_regla(usd, cot):
    raw = (usd*1.07 + FLETE_PRENDA_USD) * cot * MARGEN
    return int(round(raw/100.0))*100 - 10
if __name__=='__main__':
    junio = [(6.99,39890),(8.99,45790),(9.49,47290),(9.99,48790),(11.99,54690)]
    for u,p in junio: print(u, p, precio_sin_regla(u,1456), 'OK' if precio_sin_regla(u,1456)==p else 'X')
    for u in (2.99,4.49,7.99,11.99,16): print('hoy', u, precio(u,1560))
