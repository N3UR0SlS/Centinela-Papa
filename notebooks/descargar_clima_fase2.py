# Fase 2 - descarga el clima HORARIO de NASA POWER (2001-2025) para las dos
# celdas donde caen las fotos con GPS y lo resume a una fila por dia.
#
# Uso:
#   pip install requests pandas
#   python descargar_clima_fase2.py
#
# Deja clima_mbeya_diario.csv en la carpeta desde donde lo corres (unos 500 KB).
# Tarda unos 5 a 10 minutos: son 25 anos x 2 celdas = 50 consultas a la API.
#
# Por que horario y no diario: el criterio de Hutton (alerta de tizon tardio)
# pide contar HORAS con humedad relativa >= 90 %, y eso solo sale del horario.

import time
import requests
import pandas as pd

# Centros de celda NASA POWER (0,5 lat x 0,625 lon). Salen del manifiesto:
# 195 fotos con GPS en (-9,0 / 33,75) y 7 en (-9,0 / 33,125).
CELDAS = [(-9.0, 33.75), (-9.0, 33.125)]
ANIO_INI, ANIO_FIN = 2001, 2025
PARAMS = "T2M,RH2M,PRECTOTCORR,WS2M"
URL = "https://power.larc.nasa.gov/api/temporal/hourly/point"


def bajar_anio(lat, lon, anio, intentos=4):
    q = {"parameters": PARAMS, "community": "AG", "latitude": lat,
         "longitude": lon, "start": f"{anio}0101", "end": f"{anio}1231",
         "format": "JSON", "time-standard": "LST"}   # hora local de Tanzania
    for k in range(intentos):
        try:
            r = requests.get(URL, params=q, timeout=120)
            r.raise_for_status()
            p = r.json()["properties"]["parameter"]
            df = pd.DataFrame(p)
            df.index = pd.to_datetime(df.index, format="%Y%m%d%H")
            return df
        except Exception as e:
            print(f"   intento {k + 1} fallo ({e}); reintento...")
            time.sleep(5 * (k + 1))
    raise SystemExit(f"No pude bajar {anio} en ({lat}, {lon}).")


def resumir_dia(h):
    h = h.replace(-999, pd.NA).astype(float)
    d = pd.DataFrame({
        "t_media": h["T2M"].resample("D").mean(),
        "t_min": h["T2M"].resample("D").min(),
        "t_max": h["T2M"].resample("D").max(),
        "hr_media": h["RH2M"].resample("D").mean(),
        "hr_max": h["RH2M"].resample("D").max(),
        "horas_hr90": (h["RH2M"] >= 90).resample("D").sum(),
        "lluvia_mm": h["PRECTOTCORR"].resample("D").sum(),
        "viento_ms": h["WS2M"].resample("D").mean(),
        "horas_validas": h["T2M"].resample("D").count(),
    })
    return d


partes = []
for lat, lon in CELDAS:
    print(f"Celda ({lat}, {lon})")
    for anio in range(ANIO_INI, ANIO_FIN + 1):
        h = bajar_anio(lat, lon, anio)
        d = resumir_dia(h)
        d["celda_lat"], d["celda_lon"] = lat, lon
        partes.append(d)
        print(f"   {anio}: {len(h)} horas -> {len(d)} dias")
        time.sleep(1)

clima = pd.concat(partes).rename_axis("fecha").reset_index()
clima["fecha"] = clima["fecha"].dt.strftime("%Y-%m-%d")
clima = clima.round(3)
clima.to_csv("clima_mbeya_diario.csv", index=False)

print("\nListo: clima_mbeya_diario.csv")
print("Filas:", len(clima), "| dias con <24 horas validas:",
      int((clima["horas_validas"] < 24).sum()))
print(clima.groupby(["celda_lat", "celda_lon"])[["t_min", "hr_media", "horas_hr90"]].mean().round(2))
