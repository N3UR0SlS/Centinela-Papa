# Extrae los rasgos de color y textura de las fotos de papa, en tu computador,
# leyendo directo de los tres zips de Zenodo. Genera rasgos_papa.csv (pocos MB),
# que luego usa el cuaderno de la Fase 1 en Colab sin descargar nada pesado.
#
# Uso:
#   pip install pillow numpy pandas
#   Ajusta CARPETA (donde estan healthy.zip, earlyblt.zip y lateblt.zip)
#   python extraer_rasgos.py
#
# El CSV no guarda coordenadas: solo rasgos, clase, fecha de la toma y si la
# foto tiene GPS (si/no). Es la misma logica de la seccion 1 del cuaderno.

import io, os, zipfile, random, json, time
from collections import Counter
import numpy as np, pandas as pd
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

CARPETA   = r"C:\Users\ASUS\Downloads"   # <-- donde estan los tres zips
POR_CLASE = 1500                          # None = todas las fotos (58.709; tarda mas)
LADO      = 128
SEMILLA   = 42
ZIPS = {"sana": ("healthy.zip", 0), "temprano": ("earlyblt.zip", 1), "tardio": ("lateblt.zip", 1)}
COLUMNAS = ["R_media","G_media","B_media","R_std","G_std","B_std",
            "exg_media","necrosis_frac","brillo_media","textura"]

def rasgos_imagen(img, lado=LADO):
    a = np.asarray(img.convert("RGB").resize((lado, lado)), dtype=np.float32)
    R, G, B = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    gris = 0.299 * R + 0.587 * G + 0.114 * B
    exg = 2 * G - R - B
    necrosis = float(np.mean((R > G) & (R > B)))
    gx, gy = np.gradient(gris)
    textura = float(np.std(np.sqrt(gx ** 2 + gy ** 2)))
    return [R.mean(), G.mean(), B.mean(), R.std(), G.std(), B.std(),
            float(exg.mean()), necrosis, float(gris.mean()), textura]

def es_imagen_real(n):
    base = n.split("/")[-1]
    return (n.lower().endswith((".jpg", ".jpeg", ".png"))
            and "__MACOSX" not in n and not base.startswith("._"))

def meta_exif(img):
    try:
        ex = img._getexif() or {}
    except Exception:
        ex = {}
    f = ex.get(36867)
    return (f.split(" ")[0].replace(":", "-") if f else ""), int(34853 in ex)

filas, stats, t0 = [], {}, time.time()
for clase, (nombre, etiqueta) in ZIPS.items():
    errores, ok = Counter(), 0
    with zipfile.ZipFile(os.path.join(CARPETA, nombre)) as z:
        todos = [n for n in z.namelist() if n.lower().endswith((".jpg", ".jpeg", ".png"))]
        nombres = [n for n in todos if es_imagen_real(n)]
        basura = len(todos) - len(nombres)
        random.Random(SEMILLA).shuffle(nombres)
        if POR_CLASE: nombres = nombres[:POR_CLASE]
        for i, n in enumerate(nombres, 1):
            try:
                img = Image.open(io.BytesIO(z.read(n)))
                fecha, gps = meta_exif(img)
                filas.append(rasgos_imagen(img) + [etiqueta, clase, fecha, gps]); ok += 1
            except Exception as e:
                errores[type(e).__name__] += 1
            if i % 500 == 0:
                print(f"  {clase}: {i}/{len(nombres)}  ({time.time() - t0:.0f} s)")
    stats[clase] = {"entradas_jpg": len(todos), "basura_no_imagen": basura,
                    "intentadas": len(nombres), "ok": ok, "errores": dict(errores)}
    print(f"{clase}: {ok} de {len(nombres)} fotos OK | archivos que no son imagen: {basura} | errores: {dict(errores)}")

df = pd.DataFrame(filas, columns=COLUMNAS + ["enferma", "clase", "fecha", "tiene_gps"])
df.to_csv("rasgos_papa.csv", index=False)
json.dump(stats, open("auditoria_extraccion.json", "w"), indent=1)
print(f"\nListo: rasgos_papa.csv con {len(df)} filas y auditoria_extraccion.json ({time.time() - t0:.0f} s)")
