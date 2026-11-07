# Prepara las imagenes de la Fase 2 en tu computador, a partir de los tres zips de Zenodo.
#
# Que hace:
#   1. Lee la fecha (EXIF) de todas las fotos reales (ignora los __MACOSX).
#   2. Toma una muestra estratificada por clase MAS las fotos de los dias mixtos
#      (dias con hojas sanas y enfermas), que son las que permiten la prueba honesta.
#   3. Reduce cada foto a 256x256 y la guarda SIN EXIF (sin fecha ni GPS en el archivo).
#   4. Escribe un manifiesto CSV: archivo, clase, fecha, si tenia GPS y la CELDA de NASA POWER
#      (0,5 x 0,625 grados, unos 50 km). Las coordenadas exactas nunca se guardan.
#
# Uso:
#   pip install pillow pandas
#   Ajusta CARPETA y corre:  python preparar_imagenes_fase2.py
# Resultado (en la carpeta donde lo corras):
#   imagenes_fase2.zip     -> se sube como Release en GitHub
#   manifiesto_fase2.csv   -> me lo mandas (va al repo)

import io, os, zipfile, random, time
from collections import defaultdict
import pandas as pd
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

CARPETA      = r"C:\Users\ASUS\Downloads"   # <-- donde estan los tres zips
POR_CLASE    = 1000      # muestra general por clase
TOPE_DIA_MIX = 300       # en dias mixtos, maximo de fotos por clase y dia
LADO         = 256
SEMILLA      = 42
ZIPS = {"sana": ("healthy.zip", 0), "temprano": ("earlyblt.zip", 1), "tardio": ("lateblt.zip", 1)}

def es_imagen_real(n):
    base = n.split("/")[-1]
    return (n.lower().endswith((".jpg", ".jpeg", ".png"))
            and "__MACOSX" not in n and not base.startswith("._"))

def a_grados(v, ref):
    d, m, s = [float(x) for x in v]
    g = d + m / 60 + s / 3600
    return -g if ref in ("S", "W") else g

def meta(img):
    """Devuelve (fecha 'AAAA-MM-DD', tiene_gps, celda_lat, celda_lon). Sin coordenadas exactas."""
    try:
        ex = img._getexif() or {}
    except Exception:
        ex = {}
    f = ex.get(36867)
    fecha = f.split(" ")[0].replace(":", "-") if f else ""
    gps = ex.get(34853)
    if not gps:
        return fecha, 0, None, None
    try:
        lat = a_grados(gps[2], gps[1]); lon = a_grados(gps[4], gps[3])
        return fecha, 1, round(lat / 0.5) * 0.5, round(lon / 0.625) * 0.625   # centro de celda NASA POWER
    except Exception:
        return fecha, 1, None, None

t0 = time.time()
# 1) Recorrer todas las fotos y leer solo la metadata
registros = []
for clase, (nombre, etiqueta) in ZIPS.items():
    with zipfile.ZipFile(os.path.join(CARPETA, nombre)) as z:
        nombres = [n for n in z.namelist() if es_imagen_real(n)]
        for i, n in enumerate(nombres, 1):
            try:
                img = Image.open(io.BytesIO(z.read(n)))
                fecha, tg, clat, clon = meta(img)
                registros.append(dict(zip_=nombre, ruta=n, clase=clase, enferma=etiqueta,
                                      fecha=fecha, tiene_gps=tg, celda_lat=clat, celda_lon=clon))
            except Exception:
                pass
            if i % 5000 == 0:
                print(f"  metadata {clase}: {i}/{len(nombres)} ({time.time()-t0:.0f} s)")
todo = pd.DataFrame(registros)
print("Fotos con metadata:", len(todo))

# 2) Dias mixtos y seleccion
tab = todo[todo.fecha != ""].groupby(["fecha", "enferma"]).size().unstack(fill_value=0)
mixtos = tab[(tab.get(0, 0) > 0) & (tab.get(1, 0) > 0)].index.tolist()
print("Dias mixtos:", mixtos)
rng = random.Random(SEMILLA)
elegidas = set()
for fecha in mixtos:
    for clase in ZIPS:
        idx = todo.index[(todo.fecha == fecha) & (todo.clase == clase)].tolist()
        rng.shuffle(idx); elegidas.update(idx[:TOPE_DIA_MIX])
for clase in ZIPS:
    idx = todo.index[(todo.clase == clase) & ~todo.index.isin(elegidas)].tolist()
    rng.shuffle(idx); elegidas.update(idx[:POR_CLASE])
sel = todo.loc[sorted(elegidas)].copy()
sel["dia_mixto"] = sel.fecha.isin(mixtos).astype(int)
print("Seleccionadas:", len(sel), sel.clase.value_counts().to_dict())

# 3) Reducir, quitar EXIF y empaquetar
filas = []
with zipfile.ZipFile("imagenes_fase2.zip", "w", zipfile.ZIP_STORED) as zout:
    for nombre_zip, grupo in sel.groupby("zip_"):
        with zipfile.ZipFile(os.path.join(CARPETA, nombre_zip)) as z:
            for k, r in enumerate(grupo.itertuples(), 1):
                img = Image.open(io.BytesIO(z.read(r.ruta))).convert("RGB").resize((LADO, LADO))
                b = io.BytesIO(); img.save(b, "JPEG", quality=90)           # se guarda sin EXIF
                archivo = f"{r.clase}/{r.clase}_{r.Index:06d}.jpg"
                zout.writestr(archivo, b.getvalue())
                filas.append(dict(archivo=archivo, clase=r.clase, enferma=r.enferma, fecha=r.fecha,
                                  tiene_gps=r.tiene_gps, celda_lat=r.celda_lat, celda_lon=r.celda_lon,
                                  dia_mixto=r.dia_mixto))
                if k % 1000 == 0:
                    print(f"  empaquetando {nombre_zip}: {k}/{len(grupo)} ({time.time()-t0:.0f} s)")
pd.DataFrame(filas).to_csv("manifiesto_fase2.csv", index=False)
print(f"\nListo en {time.time()-t0:.0f} s: imagenes_fase2.zip ({os.path.getsize('imagenes_fase2.zip')/1e6:.0f} MB) "
      f"y manifiesto_fase2.csv ({len(filas)} fotos)")
