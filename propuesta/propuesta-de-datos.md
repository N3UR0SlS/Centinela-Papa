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

Clave de alineación: corregimos un dato de la versión anterior. La ficha de Zenodo indica que todas las fotos se tomaron en la región de Mbeya (no en cuatro regiones), entre el 22 de noviembre de 2022 y el 8 de abril de 2023. Revisamos el EXIF de una muestra de 40 fotos (de earlyblt.zip) con el script `notebooks/revisar_exif.py`: 19 traen fecha (DateTimeOriginal) y solo 1 trae GPS; las fechas de esa muestra caen en febrero de 2023 (rango 2023-02-02 a 2023-02-15).

Conclusión: hay fecha (en cerca de la mitad de las fotos) pero no GPS confiable. Por eso la clave es por muestra a nivel (Mbeya, día): se acopla cada foto que trae fecha con el clima diario de NASA POWER de Mbeya ese día. Es un acoplamiento real y con muchas más filas distintas que el nivel de mes.

Matices honestos: cerca de la mitad de las fotos no trae fecha, así que esas no se acoplan por día (se trabajan a nivel de mes o se excluyen del subconjunto acoplado). Como el GPS está prácticamente ausente, no se recupera la ubicación de la finca (bien para la privacidad) y no aplica el acoplamiento fino por celda. La ventana total del conjunto es nov 2022 a abr 2023; las 10 filas del anexo A ya se generaron recorriendo los tres zips y cruzando cada fecha con el clima diario de NASA POWER.

## 6. Línea base

La clase mayoritaria es "enferma" (alrededor del 65%), así que esa línea base da una exactitud cercana a 0.65. También reportamos un rasgo crudo usado solo (un índice de necrosis con umbral elegido en validación). El MLP tiene que superar eso. Guardamos la partición, la semilla y las cifras para comparar en las fases siguientes.

## 7. Riesgos éticos

| Riesgo | Daño | Qué hacemos |
| --- | --- | --- |
| El conjunto es de una variedad (Shangi) y una región (Mbeya) | El modelo puede no servir en otra zona | avisar el límite, aumentar datos, recalibrar antes de usarlo en otro lado |
| Falsa alarma | fumigar sin necesidad | umbral calibrado en validación |
| Alarma omitida | perder el cultivo | priorizar el recall de "enferma" |
| GPS en el EXIF (raro: 1 de 40 en la muestra) | podría exponer la ubicación de una finca | borrar el EXIF igual, por precaución, antes de subir nada |

## 8. Referencias

- Laizer, H., Mduma, N., Machuve, D., Lyimo, T., Babirye, C., Swai, J., & Siwingwa, A. (2023). Irish Potato Imagery Dataset for Early Detection of Crop Diseases [Conjunto de datos]. Zenodo. https://doi.org/10.5281/zenodo.8286529
- Laizer, H., & Mduma, N. (2025). Irish potato imagery dataset for detection of early and late blight diseases. Data in Brief, 60, 111549. https://doi.org/10.1016/j.dib.2025.111549
- NASA. (s. f.). POWER - Prediction Of Worldwide Energy Resources [Conjunto de datos]. NASA Langley Research Center. https://power.larc.nasa.gov/

---

## Anexo A - Prueba de acoplamiento

Clave: por muestra, (Mbeya, día). La fecha sale del EXIF de cada foto (DateTimeOriginal) y el clima diario de NASA POWER para el punto de Mbeya ese día. La revisión del EXIF (ver `notebooks/revisar_exif.py`) confirmó que hay fecha en cerca de la mitad de las fotos y que no hay GPS confiable, así que la granularidad es por día, no por celda.

Las 10 filas se generaron con el script `notebooks/acoplar_anexo_a.py`, que recorre los tres zips (healthy, earlyblt, lateblt), saca la fecha del EXIF de cada foto y la cruza con el clima diario de Mbeya de NASA POWER. Son filas reales, no de ejemplo:

| N.º | Día (Mbeya) | Foto (archivo fechado) | T2M (°C) | RH2M (%) | Precip. (mm) |
| --- | --- | --- | --- | --- | --- |
| 1 | 2022-11-22 | sana/healthy722.jpg | 18.37 | 82.63 | 14.07 |
| 2 | 2023-01-08 | sana/healthy1548.jpg | 17.23 | 85.79 | 55.13 |
| 3 | 2023-01-12 | sana/healthy9869.jpg | 17.36 | 85.16 | 29.88 |
| 4 | 2023-01-15 | sana/healthy5935.jpg | 16.56 | 91.05 | 43.57 |
| 5 | 2023-01-21 | sana/healthy14418.jpg | 16.49 | 88.20 | 2.82 |
| 6 | 2023-01-27 | sana/healthy20431.jpg | 17.51 | 83.26 | 10.57 |
| 7 | 2023-02-07 | tardio/lateblt3437.jpg | 17.38 | 86.34 | 3.81 |
| 8 | 2023-02-14 | temprano/earlyblt12260.jpg | 17.39 | 90.36 | 5.58 |
| 9 | 2023-02-20 | temprano/earlyblt12133.jpg | 18.33 | 83.91 | 1.19 |
| 10 | 2023-02-24 | temprano/earlyblt2191.jpg | 18.15 | 86.59 | 9.94 |

Las fechas cubren de noviembre 2022 a febrero 2023, con humedad relativa alta (82 a 91%), que es justo la condición que favorece el tizón. El CSV completo está en `propuesta/anexo_a.csv`.

Consulta de la serie (NASA POWER diario, punto de Mbeya aprox. lat -8.90, lon 33.46):

```python
import requests
url = ("https://power.larc.nasa.gov/api/temporal/daily/point"
       "?parameters=T2M,RH2M,PRECTOTCORR&community=AG"
       "&latitude=-8.90&longitude=33.46&start=20221122&end=20230408&format=JSON")
p = requests.get(url, timeout=60).json()["properties"]["parameter"]
print(p["T2M"]["20230202"], p["RH2M"]["20230202"], p["PRECTOTCORR"]["20230202"])
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

- A. Datos personales: no hay identificadores directos. La revisión del EXIF encontró GPS en solo 1 de 40 fotos, así que la ubicación de la finca prácticamente no se expone; aun así se borra el EXIF antes de subir nada a Colab, Drive o un asistente de IA.
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
