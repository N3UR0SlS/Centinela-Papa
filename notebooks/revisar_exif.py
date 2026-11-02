# Revisa el EXIF (fecha y GPS) de una muestra de fotos del dataset de papa,
# leyendo directo del .zip sin extraer todo.
#
# Uso:
#   1. pip install pillow
#   2. Cambia la variable ZIP por la ruta del .zip que bajaste de Zenodo.
#   3. python revisar_exif.py
#
# Reporta cuantas fotos traen fecha (DateTimeOriginal) y cuantas traen GPS.
# Importante: NO imprime las coordenadas. Si hay GPS, son la ubicacion de la
# finca (dato sensible); basta con saber que existen para decidir la clave.

import zipfile, io, random
from PIL import Image
from PIL.ExifTags import TAGS

ZIP = r"C:\Users\ASUS\Downloads\earlyblt.zip"   # <-- cambia por tu ruta
N = 40                                           # cuantas fotos revisar


def es_imagen_real(n):
    base = n.split("/")[-1]
    return (n.lower().endswith((".jpg", ".jpeg", ".png"))
            and "__MACOSX" not in n and not base.startswith("._"))

z = zipfile.ZipFile(ZIP)
todos = [n for n in z.namelist() if n.lower().endswith((".jpg", ".jpeg", ".png"))]
nombres = [n for n in todos if es_imagen_real(n)]
print(f"Entradas .jpg en el zip: {len(todos)} | archivos que NO son imagen (__MACOSX/._): {len(todos) - len(nombres)} | fotos reales: {len(nombres)}")
random.seed(0)
muestra = random.sample(nombres, min(N, len(nombres)))

con_fecha, con_gps, fechas = 0, 0, []
for n in muestra:
    try:
        img = Image.open(io.BytesIO(z.read(n)))
        exif = img._getexif() or {}
    except Exception as e:
        print("No se pudo abrir:", n, type(e).__name__)
        exif = {}
    tags = {TAGS.get(k, k): v for k, v in exif.items()}
    if tags.get("DateTimeOriginal"):
        con_fecha += 1
        fechas.append(tags["DateTimeOriginal"])
    if "GPSInfo" in tags:
        con_gps += 1

print(f"Fotos revisadas:            {len(muestra)}")
print(f"Con fecha (DateTimeOriginal): {con_fecha}")
print(f"Con GPS:                      {con_gps}")
if fechas:
    print("Ejemplos de fecha:", fechas[:5])
    print("Rango de fechas:   ", min(fechas), "->", max(fechas))
else:
    print("Ninguna trae fecha: el escenario es (Mbeya, mes), casi constante.")
