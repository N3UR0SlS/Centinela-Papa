# Propuesta de Datos - Proyecto Centinela

Base de datos del proyecto (Fase 3). Se usa el formato de la compuerta de la Fase 1, que es donde se fija la política de datos; las Fases 2 y 3 reutilizan las mismas fuentes.

Integrantes: Juan Guillermo Montaño Junca y Jair Andrés Valderrama Cano. Fecha: 2026-10-30. Versión: v1.

## 1. Problema, cliente y objetivo

Queremos anticipar si una hoja de papa tiene tizón, sí o no. El cliente es un servicio de extensión agrícola que acompaña a pequeños productores y necesita decidir cuándo intervenir un lote. El tizón puede acabar con un cultivo en pocos días, así que detectarlo temprano ahorra pérdidas y fumigaciones de más.

El objetivo es binario: hoja enferma, sí o no. El conjunto trae tres clases (sana, tizón temprano, tizón tardío) y agrupamos las dos enfermas en una sola. Se pierde el tipo de tizón y la severidad, pero la decisión en campo es de todos modos un sí o un no.

## 2. Las dos modalidades

- Imagen: una foto de hoja de papa tomada con celular en campo. El instrumento es la cámara y aporta el color y la textura de las lesiones.
- Serie temporal: clima diario (temperatura, humedad, precipitación) de NASA POWER. Aporta las condiciones que favorecen el tizón.

Pregunta de control, "¿la imagen contiene algo que un número no contenga?": sí. La cámara y la estación meteorológica son instrumentos distintos y ninguno se deriva del otro.

## 3. Fuentes

| Modalidad | Fuente | Enlace / DOI | Licencia | ¿Personas? |
| --- | --- | --- | --- | --- |
| Imagen | Irish Potato Imagery Dataset (Laizer et al., Zenodo) | https://doi.org/10.5281/zenodo.8286529 | por confirmar en Zenodo | No |
| Temporal | NASA POWER | https://power.larc.nasa.gov/ | libre uso, con atribución | No |

La licencia exacta del conjunto de papa hay que leerla en la ficha de Zenodo y anotarla antes de aprobar.

## 4. Por qué no es un reto resuelto

Son 58.709 fotos de campo, con fondos e iluminación variables, no imágenes de laboratorio, así que piden un EDA real. La fuente primaria es Zenodo, no Kaggle. El tema de papa sí abunda en Kaggle vía PlantVillage, pero es otro conjunto (de laboratorio); lo declaramos y en el anexo B mostramos que nuestros archivos no coinciden y que no descargamos nada de Kaggle.

## 5. Plan de la Fase 1 y clave de alineación

En la Fase 1 aplanamos la imagen a tabla (promedios por canal R, G, B y algún descriptor de textura) y con eso entrenamos el MLP. En la Fase 2 eso se cambia por una CNN, entra la serie con una LSTM y se fusionan.

La alineación es agregada por región y mes: las fotos vienen de unas regiones y fechas conocidas, y el clima se consulta para esas mismas. La salvedad es que una foto no trae su propio dato climático, y el clima es casi constante dentro de un mes. Las 10 filas de prueba van en el anexo A.

## 6. Línea base

La clase mayoritaria es "enferma" (alrededor del 65%), así que esa línea base da una exactitud cercana a 0,65. También reportamos un rasgo crudo usado solo (un índice de necrosis con umbral elegido en validación). El MLP tiene que superar eso. Guardamos la partición, la semilla y las cifras para comparar en las fases siguientes.

## 7. Riesgos éticos

| Riesgo | Daño | Qué hacemos |
| --- | --- | --- |
| El conjunto es de una variedad y una región | El modelo puede no servir en otra zona | avisar el límite, aumentar datos, recalibrar antes de usarlo en otro lado |
| Falsa alarma | fumigar sin necesidad | umbral calibrado en validación |
| Alarma omitida | perder el cultivo | priorizar el recall de "enferma" |

## 8. Referencias

- Laizer, H., Mduma, N., Machuve, D., Lyimo, T., Babirye, C., Swai, J., & Siwingwa, A. (2023). Irish Potato Imagery Dataset for Early Detection of Crop Diseases [Conjunto de datos]. Zenodo. https://doi.org/10.5281/zenodo.8286529
- Laizer, H., & Mduma, N. (2025). Irish potato imagery dataset for detection of early and late blight diseases. Data in Brief, 60, 111549. https://doi.org/10.1016/j.dib.2025.111549
- NASA. (s. f.). POWER - Prediction Of Worldwide Energy Resources [Conjunto de datos]. NASA Langley Research Center. https://power.larc.nasa.gov/

---

## Anexo A - Prueba de acoplamiento

Clave: (región, mes). Cada fila une una foto o su conteo con el clima de NASA POWER de esa región y mes. Los valores del clima se llenan corriendo la consulta de abajo.

| N.º | (región, mes) | Dato de imagen | Clima (RH2M, T2M) |
| --- | --- | --- | --- |
| 1 | Mbeya, 2022-11 | | |
| 2 | Mbeya, 2022-12 | | |
| 3 | Mbeya, 2023-01 | | |
| 4 | Iringa, 2022-12 | | |
| 5 | Iringa, 2023-01 | | |
| 6 | Iringa, 2023-02 | | |
| 7 | Njombe, 2023-01 | | |
| 8 | Njombe, 2023-02 | | |
| 9 | Songwe, 2023-02 | | |
| 10 | Songwe, 2023-03 | | |

Consulta de la serie (NASA POWER):

```python
import requests, pandas as pd
regiones = {"Mbeya":(-8.90,33.46),"Iringa":(-7.77,35.69),
            "Njombe":(-9.34,34.77),"Songwe":(-9.00,33.00)}
filas = []
for r,(lat,lon) in regiones.items():
    url = ("https://power.larc.nasa.gov/api/temporal/monthly/point"
           f"?parameters=T2M,RH2M,PRECTOTCORR&community=AG"
           f"&latitude={lat}&longitude={lon}&start=2022&end=2023&format=JSON")
    p = requests.get(url, timeout=60).json()["properties"]["parameter"]
    for ym in ["202211","202212","202301","202302","202303","202304"]:
        filas.append({"region":r,"mes":ym,"T2M":p["T2M"].get(ym),
                      "RH2M":p["RH2M"].get(ym),"PRECTOTCORR":p["PRECTOTCORR"].get(ym)})
print(pd.DataFrame(filas))
```

## Anexo B - Test de procedencia

- Los tres .zip se descargan del DOI de Zenodo y se les calcula el SHA-256 con hashlib.
- En el cuaderno no hay nada de Kaggle (se verifica con un grep "kaggle").
- Búsqueda de espejos (2026-10-30): el espejo conocido es Hugging Face (Project-AgML), con el mismo origen Zenodo. PlantVillage, que está en Kaggle, es otro conjunto.
- Crudeza: 58.709 imágenes en 3 clases (sana 20.438, temprano 17.772, tardío 20.499); faltantes a reportar tras cargar.
- Contraste con PlantVillage: SHA-256 distinta, imágenes de campo y no de laboratorio.

## Anexo C - Protección de datos

En las dos fuentes no hay datos de personas: son hojas de papa y clima agregado por zona. El único cuidado es borrar los metadatos EXIF/GPS de las fotos antes de subirlas. Los datos quedan locales (en .gitignore) y un script los descarga de la fuente primaria. La licencia del dataset queda por confirmar en Zenodo.

Declaramos que lo anterior es cierto y se revisó para cada fuente.

| Integrante | Firma | Fecha |
| --- | --- | --- |
| Juan Guillermo Montaño Junca | | |
| Jair Andrés Valderrama Cano | | |
