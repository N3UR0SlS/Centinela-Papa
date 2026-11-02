# Arma las 10 filas del Anexo A: cruza las fechas (EXIF) de las fotos con el
# clima diario de NASA POWER para Mbeya. Guarda el resultado en anexo_a.csv.
#
# Uso:
#   pip install pillow requests
#   Ajusta las rutas de ZIPS con los tres archivos que bajaste de Zenodo.
#   python acoplar_anexo_a.py
#
# Solo usa la fecha (DateTimeOriginal); no toca ni imprime coordenadas.

import zipfile, io, csv
import requests
from PIL import Image
from PIL.ExifTags import TAGS

ZIPS = {
    "sana":     r"C:\Users\ASUS\Downloads\healthy.zip",
    "temprano": r"C:\Users\ASUS\Downloads\earlyblt.zip",
    "tardio":   r"C:\Users\ASUS\Downloads\lateblt.zip",
}
LAT, LON = -8.90, 33.46   # Mbeya
N_FILAS = 10


def es_imagen_real(n):
    base = n.split("/")[-1]
    return (n.lower().endswith((".jpg", ".jpeg", ".png"))
            and "__MACOSX" not in n and not base.startswith("._"))

# 1. Un archivo de ejemplo por cada dia con fecha EXIF
por_dia = {}
for clase, ruta in ZIPS.items():
    try:
        z = zipfile.ZipFile(ruta)
    except FileNotFoundError:
        print("No encontre:", ruta)
        continue
    for n in z.namelist():
        if not es_imagen_real(n):
            continue
        try:
            exif = Image.open(io.BytesIO(z.read(n)))._getexif() or {}
        except Exception:
            continue
        tags = {TAGS.get(k, k): v for k, v in exif.items()}
        fecha = tags.get("DateTimeOriginal")
        if not fecha:
            continue
        dia = fecha.split(" ")[0].replace(":", "-")   # 2023-02-15
        por_dia.setdefault(dia, f"{clase}/{n.split('/')[-1]}")

dias_ord = sorted(por_dia)
if not dias_ord:
    raise SystemExit("Ninguna foto trae fecha: la clave cae a (Mbeya, mes).")

# Tomar N dias repartidos a lo largo de la ventana
if len(dias_ord) <= N_FILAS:
    dias = dias_ord
else:
    paso = len(dias_ord) / N_FILAS
    dias = [dias_ord[int(i * paso)] for i in range(N_FILAS)]

# 2. Clima diario de NASA POWER en la ventana observada
ini, fin = dias_ord[0].replace("-", ""), dias_ord[-1].replace("-", "")
url = ("https://power.larc.nasa.gov/api/temporal/daily/point"
       f"?parameters=T2M,RH2M,PRECTOTCORR&community=AG"
       f"&latitude={LAT}&longitude={LON}&start={ini}&end={fin}&format=JSON")
clima = requests.get(url, timeout=90).json()["properties"]["parameter"]

# 3. Tabla final
filas = []
for i, dia in enumerate(dias, 1):
    ymd = dia.replace("-", "")
    filas.append([i, f"Mbeya, {dia}", por_dia[dia],
                  clima["T2M"].get(ymd), clima["RH2M"].get(ymd), clima["PRECTOTCORR"].get(ymd)])

print(f"{'N':>2}  {'dia':<12} {'foto':<26} T2M    RH2M   PRECTOT")
for f in filas:
    print(f"{f[0]:>2}  {f[1]:<12} {f[2]:<26} {f[3]}  {f[4]}  {f[5]}")

with open("anexo_a.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["N", "clave", "foto", "T2M", "RH2M", "PRECTOTCORR"])
    w.writerows(filas)
print("\nGuardado en anexo_a.csv")
