# Centinela de la Papa

Sistema de alerta temprana de tizón (early/late blight) en cultivos de papa de pequeños productores.

Proyecto Centinela (Fase 1, versión v1) del curso Profundización I - Redes Neuronales (Deep Learning), código EA-N-F-004, Maestría en Ciencia de Datos, Universidad Santo Tomás. El proyecto es longitudinal: la Propuesta de Datos de esta Fase 1 fija las fuentes que se reutilizan en las Fases 2 y 3.

## Autores

- Juan Guillermo Montaño Junca
- Jair Andrés Valderrama Cano

## Estado

Fase de aprobación (compuerta / Propuesta de Datos), versión v1 ajustada tras la retroalimentación del docente. Los datos todavía no se han descargado; en esta etapa solo se define y sustenta la propuesta. La descarga y verificación de las fuentes se hará en la etapa siguiente.

## De qué trata

El sistema combina dos modalidades reales para anticipar el riesgo de tizón en papa:

- Rama de imagen: fotos de hoja de papa capturadas con teléfono en campo; una CNN decide "hoja enferma: sí/no". Más adelante (Fase 3) esta rama se industrializa para correr offline en una tablet con LiteRT.
- Rama temporal: variables climáticas diarias (temperatura, humedad, precipitación) de NASA POWER, que es un producto satelital y de reanálisis, no una estación meteorológica. Aporta las condiciones de riesgo y se sirve por API REST en la nube.

Las dos ramas se fusionan en una sola predicción de alerta.

## Estructura del repositorio

```
centinela-papa/
├── README.md                     Este archivo
├── .gitignore
├── propuesta/
│   ├── propuesta-de-datos.md     Propuesta de Datos (compuerta, Paso 0)
│   └── Propuesta_de_Datos_Centinela_Papa.pdf
├── notebooks/                    Cuadernos (próxima etapa)
├── data/                         Datos descargados (ignorados por git)
└── docs/
    └── historia-foro.md          Narrativa del proyecto para el foro
```

## Fuentes de datos (declaradas, aún sin descargar)

| Modalidad | Fuente | Enlace / DOI | Licencia |
| --- | --- | --- | --- |
| Imagen | Irish Potato Imagery Dataset for Early Detection of Crop Diseases (Laizer et al., Zenodo) | https://doi.org/10.5281/zenodo.8286529 | CC BY 4.0 |
| Temporal | NASA POWER (Prediction Of Worldwide Energy Resources) | https://power.larc.nasa.gov/ | libre uso, con atribución |

## Reproducibilidad

- Los datos no se versionan en el repo. La carpeta `data/` está en `.gitignore`.
- La partición será por grupo (finca o fecha), no por foto, para evitar casi duplicados entre entrenamiento y prueba.
- En la etapa siguiente se incluirá un script que descarga las imágenes desde Zenodo y la serie climática desde la API de NASA POWER, para que el cuaderno corra de principio a fin.
- El repositorio es privado y compartido con el docente (o público con el script de descarga y sin datos personales), según la regla de entrega de la rúbrica.

## Pendiente antes de cerrar el Anexo A

Revisar el EXIF de una muestra de fotos (campo DateTimeOriginal y coordenadas). Si solo hay región y mes, la clave de alineación es (Mbeya, mes) y es casi constante; si hay GPS, se acopla cada foto con la celda de NASA POWER (unos 50 km) por día, lo que además protege la ubicación de las fincas.
