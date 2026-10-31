# Centinela de la Papa

Sistema de alerta temprana de tizón (early/late blight) en cultivos de papa de pequeños productores.

Proyecto Centinela (Fase 3) del curso **Profundización I - Redes Neuronales (Deep Learning)**, código EA-N-F-004, Maestría en Ciencia de Datos, Universidad Santo Tomás.

## Autores

- Juan Guillermo Montaño Junca
- Jair Andrés Valderrama Cano

## Estado

Fase temprana de **aprobación (compuerta / Propuesta de Datos)**. Los datos todavía **no se han descargado**; en esta etapa solo se define y sustenta la propuesta. La descarga y verificación de las fuentes se hará en la siguiente etapa.

## De qué trata

El sistema combina dos modalidades reales para anticipar el riesgo de tizón en papa:

- **Rama de imagen (visión):** fotos de hoja de papa capturadas con teléfono en campo; una CNN decide "hoja enferma: sí/no". En la Fase 3 esta rama se industrializa para correr **offline en una tablet** con LiteRT.
- **Rama temporal (serie):** variables meteorológicas diarias (temperatura, humedad, precipitación) de NASA POWER; una RNN/LSTM aporta la señal de condiciones de riesgo. Se sirve por **API REST en la nube**.

Las dos ramas se fusionan en una sola predicción de alerta.

## Estructura del repositorio

```
centinela-papa/
├── README.md                     Este archivo
├── .gitignore
├── propuesta/
│   └── propuesta-de-datos.md     Propuesta de Datos (compuerta, Paso 0)
├── notebooks/                    Cuadernos de la Fase 3 (próxima etapa)
├── data/                         Datos descargados (ignorados por git)
└── docs/
    └── historia-foro.md          Narrativa del proyecto para el foro
```

## Fuentes de datos (declaradas, aún sin descargar)

| Modalidad | Fuente | Enlace / DOI |
| --- | --- | --- |
| Imagen | Irish Potato Imagery Dataset for Early Detection of Crop Diseases (Laizer et al., Zenodo) | https://doi.org/10.5281/zenodo.8286529 |
| Temporal | NASA POWER (Prediction Of Worldwide Energy Resources) | https://power.larc.nasa.gov/ |

## Reproducibilidad

- Los datos **no se versionan en el repo**. La carpeta `data/` está en `.gitignore`.
- En la etapa siguiente se incluirá un script que descarga las imágenes desde Zenodo y la serie climática desde la API de NASA POWER, para que el cuaderno corra de principio a fin.
- El repositorio es privado y compartido con el docente (o público con el script de descarga y sin datos personales), según la regla de entrega de la rúbrica.

## Pendientes antes de aprobar la compuerta

1. Confirmar y anotar la **licencia** exacta del dataset de papa en la ficha de Zenodo del DOI.
2. Llenar el **Anexo A** (10 filas reales) ejecutando la consulta a NASA POWER incluida en la propuesta.
