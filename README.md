# Centinela de la Papa

Sistema de alerta temprana de tizón (early/late blight) en cultivos de papa de pequeños productores.

Proyecto Centinela (Fase 1, versión v1) del curso Profundización I - Redes Neuronales (Deep Learning), código EA-N-F-004, Maestría en Ciencia de Datos, Universidad Santo Tomás. El proyecto es longitudinal: la Propuesta de Datos de esta Fase 1 fija las fuentes que se reutilizan en las Fases 2 y 3.

## Autores

- Juan Guillermo Montaño Junca
- Jair Andrés Valderrama Cano

## Entregables de la Fase 1

| Entregable | Archivo |
| --- | --- |
| Cuaderno (corre con "Ejecutar todo" en Colab) | [`notebooks/01_centinela_fase1_papa.ipynb`](notebooks/01_centinela_fase1_papa.ipynb) |
| Cuaderno ya ejecutado, con todas las salidas | [`notebooks/01_centinela_fase1_papa_ejecutado.ipynb`](notebooks/01_centinela_fase1_papa_ejecutado.ipynb) |
| Informe técnico-ético (PDF, 4 páginas) | [`Informe/Informe Fase 1 Centinela Papa.pdf`](Informe/Informe%20Fase%201%20Centinela%20Papa.pdf) |
| Propuesta de Datos (compuerta, Paso 0) | [`propuesta/Propuesta_de_Datos_Centinela_Papa.pdf`](propuesta/Propuesta_de_Datos_Centinela_Papa.pdf) |
| Bitácora de IA y auditoría | Anexos A y C del cuaderno |

**Cómo ejecutarlo:** abrir el cuaderno en Google Colab (Archivo → Abrir cuaderno → GitHub → `N3UR0SlS/Centinela-Papa`) y Ejecutar todo. El cuaderno baja de este repositorio los rasgos ya extraídos (`datos_derivados/rasgos_papa.csv`, 58.707 fotos), así que corre en pocos minutos sin descargar las imágenes. Si ese archivo no está, descarga los zips de Zenodo y los reconstruye.

## De qué trata

El sistema combina dos modalidades reales para anticipar el riesgo de tizón en papa:

- Rama de imagen: fotos de hoja de papa capturadas con teléfono en campo; una CNN decide "hoja enferma: sí/no". Más adelante (Fase 3) esta rama se industrializa para correr offline en una tablet con LiteRT.
- Rama temporal: variables climáticas diarias (temperatura, humedad, precipitación) de NASA POWER, que es un producto satelital y de reanálisis, no una estación meteorológica. Aporta las condiciones de riesgo y se sirve por API REST en la nube.

Las dos ramas se fusionan en una sola predicción de alerta.

## Estructura del repositorio

```
Centinela-Papa/
├── README.md
├── Informe/                       Informe técnico-ético de la Fase 1 (Word y PDF)
├── propuesta/                     Propuesta de Datos (md y PDF) y anexo_a.csv
├── notebooks/
│   ├── 01_centinela_fase1_papa.ipynb            cuaderno de la Fase 1
│   ├── 01_centinela_fase1_papa_ejecutado.ipynb  el mismo, con salidas
│   ├── extraer_rasgos.py          extrae los rasgos desde los zips de Zenodo
│   ├── revisar_exif.py            revisa fecha y GPS en el EXIF
│   └── acoplar_anexo_a.py         cruza fechas con NASA POWER (anexo A)
├── datos_derivados/               rasgos_papa.csv y auditoría de la extracción
├── data/                          datos crudos locales (ignorados por git)
└── docs/historia-foro.md          presentación del proyecto en el foro
```

## Fuentes de datos

| Modalidad | Fuente | Enlace / DOI | Licencia |
| --- | --- | --- | --- |
| Imagen | Irish Potato Imagery Dataset for Early Detection of Crop Diseases (Laizer et al., Zenodo) | https://doi.org/10.5281/zenodo.8286529 | CC BY 4.0 |
| Temporal | NASA POWER (Prediction Of Worldwide Energy Resources) | https://power.larc.nasa.gov/ | libre uso, con atribución |

## Reproducibilidad

- Los datos no se versionan en el repo. La carpeta `data/` está en `.gitignore`.
- La partición será por grupo (finca o fecha), no por foto, para evitar casi duplicados entre entrenamiento y prueba.
- `notebooks/extraer_rasgos.py` reconstruye `datos_derivados/rasgos_papa.csv` desde los zips de Zenodo; el cuaderno hace lo mismo si el CSV no está.
- `datos_derivados/` contiene un derivado sin imágenes ni coordenadas (licencia CC BY 4.0 de la fuente, con atribución).
- El repositorio es privado y compartido con el docente (o público con el script de descarga y sin datos personales), según la regla de entrega de la rúbrica.

## Clave de alineación (resuelta)

La revisión del EXIF (`notebooks/revisar_exif.py`) mostró que todas las fotos traen fecha y cerca de un tercio trae GPS, así que la clave es (Mbeya, día): cada foto se cruza con el clima diario de NASA POWER. Ojo: la mitad de las entradas de cada zip son archivos `__MACOSX` que no son imágenes, y las clases se fotografiaron en semanas distintas (posible atajo por fecha, medido en el cuaderno de la Fase 1). Las 10 filas del Anexo A se generaron con `notebooks/acoplar_anexo_a.py` y están en `propuesta/anexo_a.csv`.
