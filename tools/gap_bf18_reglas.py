"""Reglas compartidas GAP 18/11 (las usan gap_bf18.py y revision/revisar.py)."""
import re
LICENCIA = re.compile(r'disney|mickey|minnie|marvel|spider|frozen|barbie|pok[eé]mon|bluey|star wars|paw patrol|sesame|sonic|hello kitty|peppa|minecraft|harry potter|mario|looney|snoopy|peanuts|batman|superman|cocomelon', re.I)
def precio_gap(usd):
    import precio as P
    P.MARGEN = 1.7; p = P.precio(usd, P.COT); p = 29900 if 30300 <= p <= 35000 else p
    for lo, hi, v in [(0, 10, 39900), (10, 12, 42900), (12, 13, 44900)]:
        if lo <= usd < hi: p = min(p, v)
    return p
