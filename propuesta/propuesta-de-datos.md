# Propuesta de Datos - Proyecto Centinela

Propuesta de Datos de la Fase 1 (Paso 0, compuerta de aprobación). Es donde se fija la política de datos del proyecto; las Fases 2 y 3 reutilizan estas mismas fuentes.

Integrantes: Juan Guillermo Montaño Junca y Jair Andrés Valderrama Cano. Fecha: 2026-11-02. Versión: v1 (ajustada tras la retroalimentación de la compuerta).

## 1. Problema, cliente y objetivo

Queremos anticipar si una hoja de papa tiene tizón, sí o no. El cliente es un servicio de extensión agrícola que acompaña a pequeños productores y necesita decidir cuándo intervenir un lote. El tizón puede acabar con un cultivo en pocos días, así que detectarlo temprano ahorra pérdidas y fumigaciones de más.

El objetivo es binario: hoja enferma, sí o no. El conjunto trae tres clases (sana, tizón temprano, tizón tardío) y agrupamos las dos enfermas en una sola. Se pierde el tipo de tizón y la severidad, pero la decisión en campo es de todos modos un sí o un no.

## 2. Las dos modalidades

- Imagen: una foto de hoja de papa tomada con celular en campo. El instrumento es la cámara y aporta el color y la textura de las lesiones.
- Serie temporal: clima diario (temperatura, humedad, precipitación) de NASA POWER, que es un producto satelital y de reanálisis (no una estación meteorológica). Aporta las condiciones que favorecen el tizón.

Pregunta de control, "¿la imagen contiene algo que un número no contenga?": sí. La cámara, que capta el estado real de la hoja, y NASA POWER, que es un producto satelital y de reanálisis del clima, son dos fuentes físicamente independientes; ninguna se deriva de la otra.

## 3. Fuentes

| Modalidad | Fuente | Enlace / DOI | Licencia | Dónde se verificó | ¿Personas? |
| --- | --- | --- | --- | --- | --- |
| Imagen | Irish Potato Imagery Dataset (Laizer et al., Zenodo) | https://doi.org/10.5281/zenodo.8286529 | CC BY 4.0 | ficha de Zenodo del DOI | No |
| Temporal | NASA POWER | https://power.larc.nasa.gov/ | libre uso, con atribución | página de la fuente | No |

## 4. Por qué no es un reto resuelto

Son 58.709 fotos de campo, con fondos e iluminación variables, no imágenes de laboratorio, así que piden un EDA real. La fuente primaria es Zenodo, no Kaggle. El tema de papa sí abunda en Kaggle vía PlantVillage, pero es otro conjunto (de laboratorio); lo declaramos y en el anexo B mostramos que nuestros archivos no coinciden y que no descargamos nada de Kaggle.

## 5. Plan de la Fase 1, clave de alineación y partición

En la Fase 1 aplanamos la imagen a tabla (promedios por canal R, G, B y algún descriptor de textura) y con eso entrenamos el MLP. En la Fase 2 eso se cambia por una CNN, entra la serie con una LSTM y se fusionan.

Partición por grupo: como hay muchas fotos de las mismas fincas y fechas, la partición se hace por grupo (finca o fecha), no por foto, para que no queden casi duplicados repartidos entre entrenamiento y prueba (por ejemplo GroupShuffleSplit o StratifiedGroupKFold). Partir por foto inflaría el desempeño de forma engañosa.

Clave de alineación: corregimos un dato de la versión anterior. La ficha de Zenodo indica que todas las fotos se tomaron en la región de Mbeya (no en cuatro regiones), entre el 22 de noviembre de 2022 y el 8 de abril de 2023. Antes de llenar el anexo A revisamos en una muestra de fotos el EXIF (campo DateTimeOriginal y coordenadas), y de ahí sale la granularidad de la clave:

- Si solo hay región y mes: la clave es (Mbeya, mes). Deja unos 5 o 6 valores de clima para las 58.709 fotos, es casi constante, y así se declara (es una limitación honesta del acoplamiento).
- Si el EXIF trae GPS: acoplamos cada foto con la celda de NASA POWER que le corresponde (unos 50 km) por día o semana. Generalizar las coordenadas a esa celda no pierde información del clima y, de paso, protege la ubicación de las fincas.

Las 10 filas del anexo A se llenan según lo que arroje esa revisión del EXIF.

## 6. Línea base

La clase mayoritaria es "enferma" (alrededor del 65%), así que esa línea base da una exactitud cercana a 0.65. También reportamos un rasgo crudo usado solo (un índice de necrosis con umbral elegido en validación). El MLP tiene que superar eso. Guardamos la partición, la semilla y las cifras para comparar en las fases siguientes.

## 7. Riesgos éticos

| Riesgo | Daño | Qué hacemos |
| --- | --- | --- |
| El conjunto es de una variedad (Shangi) y una región (Mbeya) | El modelo puede no servir en otra zona | avisar el límite, aumentar datos, recalibrar antes de usarlo en otro lado |
| Falsa alarma | fumigar sin necesidad | umbral calibrado en validación |
| Alarma omitida | perder el cultivo | priorizar el recall de "enferma" |
| GPS en el EXIF de las fotos | expone la ubicación de la finca | borrar el EXIF/GPS antes de subir nada; generalizar coordenadas a la celda |

## 8. Referencias

- Laizer, H., Mduma, N., Machuve, D., Lyimo, T., Babirye, C., Swai, J., & Siwingwa, A. (2023). Irish Potato Imagery Dataset for Early Detection of Crop Diseases [Conjunto de datos]. Zenodo. https://doi.org/10.5281/zenodo.8286529
- Laizer, H., & Mduma, N. (2025). Irish potato imagery dataset for detection of early and late blight diseases. Data in Brief, 60, 111549. https://doi.org/10.1016/j.dib.2025.111549
- NASA. (s. f.). POWER - Prediction Of Worldwide Energy Resources [Conjunto de datos]. NASA Langley Research Center. https://power.larc.nasa.gov/

---

## Anexo A - Prueba de acoplamiento

Clave: (Mbeya, mes) en el escenario conservador; (celda de NASA POWER de unos 50 km, día o semana) si el EXIF trae GPS. Queda pendiente revisar el EXIF de una muestra antes de fijar la granularidad y llenar las filas con valores reales. El clima se obtiene con la consulta de abajo; la columna de imagen sale de agrupar las fotos por mes (o por celda y día) una vez leído el EXIF.

Escenario conservador (todo Mbeya, por mes), ventana nov 2022 a abr 2023:

| N.º | (región, mes) | Dato de imagen (fotos del mes) | Clima (T2M, RH2M, PRECTOTCORR) |
| --- | --- | --- | --- |
| 1 | Mbeya, 2022-11 | | |
| 2 | Mbeya, 2022-12 | | |
| 3 | Mbeya, 2023-01 | | |
| 4 | Mbeya, 2023-02 | | |
| 5 | Mbeya, 2023-03 | | |
| 6 | Mbeya, 2023-04 | | |

Nota: con la clave por mes solo salen estas 5 o 6 filas y el clima es casi constante entre ellas. Llegar a 10 filas reales (y a un acoplamiento con sentido) exige el escenario con GPS, por celda y día.

Consulta de la serie (NASA POWER, punto de Mbeya aprox. lat -8.90, lon 33.46):

```python
import requests, pandas as pd
url = ("https://power.larc.nasa.gov/api/temporal/monthly/point"
       "?parameters=T2M,RH2M,PRECTOTCORR&community=AG"
       "&latitude=-8.90&longitude=33.46&start=2022&end=2023&format=JSON")
p = requests.get(url, timeout=60).json()["properties"]["parameter"]
for ym in ["202211","202212","202301","202302","202303","202304"]:
    print(ym, p["T2M"].get(ym), p["RH2M"].get(ym), p["PRECTOTCORR"].get(ym))
```

Revisión del EXIF (correr sobre una muestra antes de fijar la clave):

```python
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
def leer_exif(ruta):
    img = Image.open(ruta)
    exif = img._getexif() or {}
    datos = {TAGS.get(k, k): v for k, v in exif.items()}
    return {"fecha": datos.get("DateTimeOriginal"), "gps": datos.get("GPSInfo")}
# revisar 20-30 fotos de cada clase y ver si hay fecha y coordenadas
```

## Anexo B - Test de procedencia

- Los tres .zip (healthy, earlyblt, lateblt) se descargan del DOI de Zenodo y se les calcula el SHA-256 con hashlib.
- En el cuaderno no hay nada de Kaggle (se verifica con un grep "kaggle").
- Búsqueda de espejos (2026-11-02): el espejo conocido es Hugging Face (Project-AgML), con el mismo origen Zenodo. PlantVillage, que está en Kaggle, es otro conjunto (de laboratorio).
- Crudeza: 58.709 imágenes en 3 clases (sana 20.438, temprano 17.772, tardío 20.499); faltantes a reportar tras cargar.
- Contraste con PlantVillage: SHA-256 distinta, imágenes de campo y no de laboratorio.

## Anexo C - Protección de datos

### Fuente 1: Irish Potato Imagery Dataset (Zenodo, CC BY 4.0)

Resultado: sin datos de personas (son hojas de papa). Un cuidado: el EXIF de las fotos de celular puede traer coordenadas, que son un identificador indirecto de la finca.

- A. Datos personales: no hay identificadores directos. Posible identificador indirecto: GPS en el EXIF. Mitigación: se borra el EXIF/GPS antes de subir nada a Colab, Drive o un asistente de IA, y las coordenadas se generalizan a la celda.
- B. Datos sensibles: no hay (salud humana, biométricos, etc.).
- C. Menores: no aplica, no hay personas.
- D. Base legal: fuente pública con DOI y licencia citable (CC BY 4.0); se cumple la atribución.
- E. Finalidad: uso académico para entrenar y evaluar un modelo en el curso; no se deciden cosas sobre personas identificadas.
- F. Anonimización: no hay identificadores directos; se borran EXIF/GPS de las imágenes.
- G. Licencia: CC BY 4.0, verificada en la ficha de Zenodo del DOI; obliga a atribuir e indicar cambios.
- H. Transferencia internacional: a Colab, Drive y GitHub solo suben imágenes sin EXIF; a los asistentes de IA no se les pasan registros con coordenadas reales.
- I. Minimización: solo se conservan las imágenes necesarias; se declara dónde se guardan y que se borran al terminar.
- J. Publicación: repositorio privado y compartido con el docente, o público con script de descarga y sin datos sensibles (carpeta de datos en .gitignore).

### Fuente 2: NASA POWER

Resultado: sin datos de personas (clima agregado por celda geográfica, producto satelital y de reanálisis). Licencia de libre uso con la atribución que pide la fuente. Las casillas A a J se marcan como "no aplica / sin personas". Transferencia internacional: solo datos ambientales.

### Declaración

Declaramos que lo anterior es cierto y se revisó para cada fuente.

| Integrante | Firma | Fecha (AAAA-MM-DD) |
| --- | --- | --- |
| Juan Guillermo Montaño Junca | | 2026-11-02 |
| Jair Andrés Valderrama Cano | | 2026-11-02 |
