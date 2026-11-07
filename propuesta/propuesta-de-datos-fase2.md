# Propuesta de Datos v2 - Proyecto Centinela, Fase 2

Actualización de la Propuesta de Datos de la Fase 1 para el sistema multimodal. Se mantienen el problema, el cliente y las dos fuentes. Lo que cambia es que la imagen entra cruda, la serie de clima entra completa y la clave de alineación baja a nivel de foto.

Integrantes: Juan Guillermo Montaño Junca y Jair Andrés Valderrama Cano. Fecha: 2026-11-07. Versión: v2.

## 1. Problema, cliente y objetivo

El cliente es el mismo: un servicio de extensión agrícola que acompaña a pequeños productores de papa en Mbeya (Tanzania) y decide a qué lotes mandar un técnico. En la Fase 1 la pregunta era binaria (hoja enferma, sí o no). En la Fase 2 la separamos en dos:

- Rama A (imagen): qué tiene la hoja, en tres clases (sana, tizón temprano, tizón tardío).
- Rama B (serie): si en los próximos 3 días se completa un periodo de Hutton, es decir, si viene clima que favorece el tizón tardío.
- Rama C (fusión): si combinar las dos mejora la detección de hoja enferma, medido con ablación.

## 2. Qué cambia frente a la v1

| Elemento | v1 (Fase 1) | v2 (Fase 2) |
| --- | --- | --- |
| Imagen | 10 rasgos de color y textura por hoja (58.707 hojas) | foto cruda de 256 px, sin EXIF, en una muestra de 6.695 fotos |
| Serie | 10 filas de ejemplo de clima diario (Anexo A de la v1) | clima horario 2001-2025 resumido por día, en 2 celdas (18.262 filas) |
| Clave | (Mbeya, día) | (fecha de la toma, celda NASA POWER) por foto |
| Partición | estratificada por foto | imagen: 70/15/15 estratificada; serie: cronológica; fusión: además por día y dentro de días mixtos |

## 3. Fuentes

| Modalidad | Fuente | Enlace / DOI | Licencia | Cómo se obtuvo |
| --- | --- | --- | --- | --- |
| Imagen | Irish Potato Imagery Dataset (Laizer et al., Zenodo) | https://doi.org/10.5281/zenodo.8286529 | CC BY 4.0 | `notebooks/preparar_imagenes_fase2.py` sobre los tres zips originales |
| Serie | NASA POWER, API horaria (MERRA-2) | https://power.larc.nasa.gov/ | libre uso, con atribución | `notebooks/descargar_clima_fase2.py` |

Requisitos de la actividad: imagen con al menos 500 fotos en 3 categorías (tenemos 6.695 en 3) y serie con al menos 1.000 observaciones (tenemos 9.131 días por celda). Ninguna fuente viene de Kaggle.

Atribución pedida por NASA POWER: "These data were obtained from the NASA Langley Research Center (LaRC) POWER Project funded through the NASA Earth Science/Applied Science Program."

## 4. La muestra de imágenes

De las 58.707 fotos válidas tomamos 1.000 por clase al azar (semilla 42) más todas las fotos, hasta 300 por clase, de los días mixtos, que son los días en que se fotografiaron hojas sanas y enfermas a la vez. Así quedan 6.695 fotos: 3.018 sanas, 1.676 con tizón temprano y 2.001 con tizón tardío. Los días mixtos son los que permiten probar si un modelo ve la lesión o el día.

Las fotos se redujeron a 256 x 256 y se guardaron sin EXIF. Están publicadas como Release del repositorio (`datos-fase2`, 136 MB), porque GitHub no acepta archivos de más de 25 MB en un commit. El detalle de cada foto está en `datos_derivados/manifiesto_fase2.csv`, con estas columnas: archivo, clase, fecha, si tiene GPS (sí/no), celda de NASA POWER y si es de día mixto. El manifiesto no tiene coordenadas exactas.

## 5. La serie de clima

Bajamos el clima horario (temperatura, humedad relativa, lluvia y viento a 2 m) de 2001 a 2025, en hora local, para las dos celdas donde caen las fotos con GPS: (-9,0 / 33,75), la dominante, y (-9,0 / 33,125). Lo resumimos por día con estas variables: temperatura media, mínima y máxima; humedad media y máxima; horas con humedad de 90 % o más; lluvia y viento. Usamos el horario porque el criterio de Hutton cuenta horas de humedad alta, y eso no sale del dato diario. No hay faltantes y todos los días tienen 24 horas válidas.

Hallazgo del EDA: en la celda dominante, el criterio de Hutton se cumple entre el 95 y el 100 % de los días de diciembre a abril. Por eso la rama B se evalúa también por separado en los meses de transición (mayo-junio y septiembre-noviembre).

## 6. Clave de alineación

Cada foto se une con la ventana de 14 días de clima que termina el día de la toma, en su propia celda:

- Fecha: sale del EXIF (DateTimeOriginal); el 100 % de las fotos la trae.
- Celda: si la foto trae GPS con coordenadas (202 fotos), se usa su celda; si no (6.493 fotos), se asigna la celda dominante de Mbeya, y lo declaramos como supuesto.

Es un co-registro por foto, no un emparejamiento al azar. Las dos celdas no son iguales: la temperatura mínima difiere en promedio 2,8 °C, así que cruzar cada foto con su celda tiene sentido.

Limitación declarada: como la clase depende del día de la campaña (Fase 1: la fecha sola da AUC 0,998), el clima de un día puede funcionar como "código de fecha". La rama C lo mide con tres protocolos: fotos al azar, días no vistos y dentro de un mismo día.

## 7. Riesgos éticos y de datos

| Riesgo | Daño | Qué hacemos |
| --- | --- | --- |
| GPS en el EXIF | expone la ubicación de la finca | se borra el EXIF de todas las fotos; solo se guarda la celda (unos 55 x 70 km) |
| Etiqueta por carpeta, no por lesión | fotos "enfermas" sin lesión visible | revisión visual de los días mixtos; se reporta como limitación |
| Clase ligada a la fecha | el clima "predice" por reconocer el día | evaluación por días no vistos y dentro de días mixtos |
| Reanálisis en lugar de estación | humedad sobreestimada, Hutton casi siempre activo | se declara; evaluación aparte en meses de transición |
| Una región, una temporada, una variedad | no sirve en otra zona | recalibrar con fotos y clima locales antes de usarlo en otro lado |

## 8. Referencias

- Laizer, H., Mduma, N., Machuve, D., Lyimo, T., Babirye, C., Swai, J., & Siwingwa, A. (2023). Irish potato imagery dataset for early detection of crop diseases (Versión 01) [Conjunto de datos]. Zenodo. https://doi.org/10.5281/zenodo.8286529
- Laizer, H., & Mduma, N. (2025). Irish potato imagery dataset for detection of early and late blight diseases. Data in Brief, 60, 111549. https://doi.org/10.1016/j.dib.2025.111549
- NASA Langley Research Center. (2025). Prediction Of Worldwide Energy Resources (POWER), API horaria [Conjunto de datos]. https://power.larc.nasa.gov/
- Dancey, S. R. (2018). Development and implementation of a new national warning system for potato late blight in Great Britain [Tesis doctoral, University of Dundee].

---

## Anexo A - Prueba de acoplamiento (v2)

Diez fotos reales del manifiesto, cada una con el resumen de su ventana de 14 días de clima en su celda. Se generaron con el manifiesto y `datos_derivados/clima_mbeya_diario.csv`. El CSV está en `propuesta/anexo_a_fase2.csv`.

| N.º | Foto | Clase | Fecha | Celda | Origen de la celda | Tmin media 14 d (°C) | Horas HR >= 90 % (media 14 d) | Lluvia 14 d (mm) | Días Hutton en 14 d |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | sana/sana_014410.jpg | sana | 2023-01-08 | -9,000 / 33,750 | dominante | 13,3 | 13,9 | 304 | 14 |
| 2 | sana/sana_005054.jpg | sana | 2023-01-12 | -9,000 / 33,750 | dominante | 13,2 | 13,6 | 197 | 14 |
| 3 | sana/sana_004677.jpg | sana | 2023-01-12 | -9,000 / 33,125 | GPS | 15,1 | 10,9 | 184 | 14 |
| 4 | sana/sana_009229.jpg | sana | 2023-01-23 | -9,000 / 33,750 | dominante | 13,6 | 14,6 | 238 | 14 |
| 5 | tardio/tardio_046022.jpg | tardío | 2023-01-27 | -9,000 / 33,750 | GPS | 13,7 | 14,1 | 184 | 14 |
| 6 | sana/sana_007325.jpg | sana | 2023-01-30 | -9,000 / 33,750 | dominante | 13,6 | 13,9 | 93 | 14 |
| 7 | tardio/tardio_042240.jpg | tardío | 2023-01-30 | -9,000 / 33,125 | GPS | 15,6 | 11,0 | 62 | 13 |
| 8 | tardio/tardio_057122.jpg | tardío | 2023-02-02 | -9,000 / 33,750 | dominante | 13,5 | 13,7 | 131 | 14 |
| 9 | temprano/temprano_037763.jpg | temprano | 2023-02-15 | -9,000 / 33,750 | dominante | 13,8 | 15,1 | 193 | 14 |
| 10 | tardio/tardio_041720.jpg | tardío | 2023-02-23 | -9,000 / 33,750 | dominante | 13,7 | 14,9 | 110 | 14 |

Las filas 3 y 7 muestran por qué importa la celda: el mismo día, la celda vecina es unos 2 °C más cálida y tiene unas 3 horas menos de humedad alta. Las fotos de la celda vecina del 30 de enero (como la 7) son todas tardío, y eso termina siendo un atajo, analizado en la sección 4 del cuaderno.

## Anexo B - Procedencia y reproducibilidad

- Imágenes: los tres zips originales se bajaron del DOI de Zenodo; el script `preparar_imagenes_fase2.py` filtra los archivos `__MACOSX` que no son imágenes, cuenta los errores en vez de ignorarlos y deja el zip sin EXIF y el manifiesto.
- Clima: `descargar_clima_fase2.py` consulta la API horaria año por año, con reintentos, y deja `clima_mbeya_diario.csv`.
- El cuaderno `02_centinela_fase2_papa.ipynb` baja todo del repositorio y del Release en segundos (sin Drive y sin volver a Zenodo) y corre completo en Colab con GPU T4 en unos 30 minutos.
