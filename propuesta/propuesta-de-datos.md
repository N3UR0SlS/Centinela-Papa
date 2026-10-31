# Propuesta de Datos - Proyecto Centinela

**Base de datos para la Fase 3 (sistema multimodal que se industrializa).** Se diligencia con el formato de la compuerta de la Fase 1 (Paso 0), porque es ahí donde el proyecto fija su política de datos; las Fases 2 y 3 reutilizan estas mismas fuentes. Una página de texto (secciones 0 a 8) más tres anexos que no cuentan en la extensión: A. prueba de acoplamiento; B. evidencias del test de procedencia; C. checklist de protección de datos (uno por fuente).

## 0. Encabezado

| Campo | Detalle |
| --- | --- |
| Título del proyecto | **Centinela de la Papa: alerta temprana de tizón (*early/late blight*) en cultivos de papa de pequeños productores** |
| Integrantes | Juan Guillermo Montaño Junca y Jair Andrés Valderrama Cano |
| Fecha | 2026-10-30 |
| Versión | v1 |

## 1. Problema, cliente y objetivo binario

- **Evento de riesgo y cliente:** se anticipa la presencia de tizón (gota) en la hoja de papa para un servicio de extensión agrícola / una asociación de pequeños productores de papa, que necesita decidir cuándo intervenir el cultivo.
- **Impacto:** el tizón temprano (*Alternaria solani*) y el tardío (*Phytophthora infestans*) pueden arrasar un lote en pocos días; detectarlo temprano permite focalizar el control y evitar pérdidas de cosecha y fumigaciones innecesarias.
- **Objetivo binario:** **hoja con tizón: sí/no.** El conjunto trae tres clases (sana, *early blight*, *late blight*); se **agrupan** las dos enfermas en «enferma» frente a «sana». Información que se pierde: el tipo de tizón (temprano vs. tardío) y la severidad. Se justifica porque la decisión del cliente en primera línea —intervenir o no ese foco— es binaria; la distinción de tipo se deja como extensión multiclase posterior.

## 2. Las dos modalidades del sistema completo

- **Rama de imagen:** cada imagen es una **foto RGB de una hoja de papa** tomada en campo con teléfono móvil; el instrumento es la **cámara del smartphone**. Señal que aporta: la textura, el color y el patrón de las lesiones foliares (manchas concéntricas del tizón temprano, necrosis húmeda del tardío) que distinguen una hoja enferma de una sana.
- **Rama temporal:** variables **meteorológicas diarias** —temperatura a 2 m (`T2M`), humedad relativa (`RH2M`) y precipitación (`PRECTOTCORR`)— del **reanálisis satelital/observacional de NASA POWER** para la región productora, a **frecuencia diaria**. Señal: las condiciones de humedad y temperatura que gobiernan la aparición del tizón (el tardío prospera con alta humedad y temperaturas templadas).
- **Pregunta de control, «¿La imagen contiene algo que un número no contenga?»:** **Sí.** La cámara y el instrumento meteorológico son dos mediciones físicamente independientes: la foto capta el estado fitosanitario real de la hoja (no derivable de la serie climática), y la serie capta las condiciones ambientales (no derivables de la foto). Son dos modalidades reales.

## 3. Fuentes (con enlaces y licencia)

| Modalidad | Fuente (productor primario) | Enlace o DOI | Licencia y versión | Dónde se verificó la licencia | ¿Datos de personas? |
| --- | --- | --- | --- | --- | --- |
| Imagen | Irish Potato Imagery Dataset for Early Detection of Crop Diseases (Laizer et al., Zenodo) | https://doi.org/10.5281/zenodo.8286529 | **Por verificar en la ficha de Zenodo** (ver nota) | Ficha del DOI en Zenodo | No (hojas de papa) |
| Temporal | NASA POWER (Prediction Of Worldwide Energy Resources) | https://power.larc.nasa.gov/ | Datos NASA de libre uso (con la atribución que pide la fuente) | Página de la fuente | No |

> **Nota de licencia (acción obligatoria antes de aprobar):** la licencia exacta del conjunto de papa debe leerse en la ficha de Zenodo del DOI y anotarse con su nombre y versión (p. ej., CC BY 4.0). Mientras no se confirme, la condición (b) no está cerrada. NASA POWER pide incluir el agradecimiento: «The data was obtained from the NASA Langley Research Center (LaRC) POWER Project funded through the NASA Earth Science/Applied Science Program».

## 4. Por qué NO es un reto resuelto

- **Crudeza del dato.** El conjunto de papa son **58.709 imágenes de campo** (healthy 20.438, *early blight* 17.772, *late blight* 20.499) tomadas en condiciones reales —fondos, iluminación y ángulos variables— en fincas de pequeños productores, no imágenes de laboratorio sobre fondo blanco. Exige EDA real: desbalance entre clases, ruido de fondo, variaciones de escala e iluminación. La serie de NASA POWER llega como crudo diario que hay que limpiar, agregar y alinear temporalmente.
- **No proviene de Kaggle ni de una réplica.** El productor primario es **Zenodo** (y el artículo en *Data in Brief*, Laizer & Mduma, 2025). La descarga se hace de Zenodo, no de Kaggle. **Atención (riesgo real a documentar):** «potato leaf disease» está muy presente en Kaggle a través de **PlantVillage**, que es un corpus **distinto** (imágenes de laboratorio). El test de procedencia (Anexo B) debe demostrar, con la huella SHA-256 y la huella de crudeza, que el archivo usado es el de Zenodo y **no** coincide con PlantVillage ni con un espejo de Kaggle. Existe un espejo en Hugging Face (`Project-AgML/potato_leaf_blight`) con el **mismo origen** Zenodo: se declara, pero la descarga se hace de la fuente primaria.
- **No hay una solución pública que baste copiar** para este escenario concreto (alerta temprana multimodal foto + clima con despliegue *offline*): los trabajos publicados sobre este conjunto resuelven solo la clasificación de la imagen, no la fusión con la serie climática ni el despliegue en el borde.

## 5. Plan de la Fase 1, clave de alineación y prueba de acoplamiento

- **Modalidad que se modela en la Fase 1 (aplanada a tabla):** la **imagen**, resumida en rasgos tabulares por hoja (promedios de intensidad por canal R, G, B; un índice de «parduzco»/necrosis; descriptores de textura simples). Con esos rasgos se entrena el MLP de línea base para «enferma sí/no».
- **Paso a la Fase 2:** ese aplanamiento se reemplaza por la **CNN nativa** sobre la imagen cruda, y se **incorpora la rama temporal** con una **RNN/LSTM/GRU** sobre la serie climática; ambas se **fusionan** en una sola predicción.
- **Clave de alineación (se marca una):**
- [x] **Agregada**, **(región, mes)**, con su salvedad de fuga de datos y de rasgo casi constante: las imágenes se recolectaron en las regiones de **Mbeya, Iringa, Njombe y Songwe** (Tierras Altas del Sur de Tanzania) entre **2022-11-22 y 2023-04-08**; la serie de NASA POWER se consulta para esas coordenadas y ese periodo. **Salvedad:** una foto de hoja **no tiene su propio registro climático individual** (solo se conoce la región y la ventana de recolección a nivel del conjunto), y el clima es **casi constante** dentro de una misma (región, mes); por eso la alineación es agregada, no muestra a muestra.
- [ ] Por muestra, p. ej., (finca, semana).
- **Prueba de acoplamiento (obligatoria):** diez filas reales en el **Anexo A** (se producen ejecutando la consulta a NASA POWER indicada; los valores climáticos se llenan al correrla, no se inventan).
- **Si la modalidad aplanada es una serie temporal:** no aplica en la Fase 1 (se aplana la imagen). Cuando la serie entre en la Fase 2, su partición será **cronológica** y los rezagos y transformaciones se calcularán sin mirar el futuro.

## 6. Línea base comprometida

- **Clase mayoritaria:** la clase mayoritaria es **«enferma»** (38.271 / 58.709 ≈ **65,2 %**; «sana» ≈ 34,8 %). La línea base de clase mayoritaria da una exactitud ≈ **0,652**; como la clase de riesgo («enferma») es la mayoritaria, predecir todo-enferma da *recall*(enferma)=1,0 de forma trivial, así que el modelo se juzga por el *recall* y la precisión de **ambas** clases (en especial no hundir el *recall* de «sana»). Se reportan métricas por clase en el conjunto de prueba.
- **Escalar crudo** (la modalidad aplanada resume rasgos escalares): se reporta el desempeño de **un único rasgo crudo** —p. ej., un índice de necrosis/«parduzco» promedio de la hoja— usado solo, con el umbral elegido en validación. El MLP debe superarlo.
- La partición, la semilla y estas cifras se conservan: son el punto de comparación de las fases siguientes.

## 7. Riesgos éticos y protección de datos

| Riesgo | Daño para el cliente | Mitigación |
| --- | --- | --- |
| Sesgo de muestreo o representatividad | El conjunto es de **una variedad (Shangi) y una sola región** (Tanzania); el modelo puede no transferir a variedades y condiciones de otra zona (p. ej., Cundinamarca), dando falsas seguridades. | Declarar el límite de transferencia; aumentar datos (rotación, iluminación, fondos); validar en un subconjunto separado por región; recomendar recalibración antes de usarlo en otra zona. |
| Falsa alarma (predecir tizón donde no lo hay) | Fumigación innecesaria: costo económico y ambiental, resistencia del patógeno. | Umbral de decisión calibrado en validación según el costo relativo de los errores; reportar la tasa de falsos positivos. |
| Alarma omitida (no detectar un brote real) | Pérdida de cultivo por intervención tardía. | Priorizar el *recall* de la clase «enferma»; elegir el umbral penalizando los falsos negativos; combinar con la señal climática en la fusión. |

El checklist de protección de datos va en el **Anexo C**, uno por fuente.

## 8. Cita APA 7 de cada fuente

- Laizer, H., Mduma, N., Machuve, D., Lyimo, T., Babirye, C., Swai, J., & Siwingwa, A. (2023). *Irish Potato Imagery Dataset for Early Detection of Crop Diseases* (Versión 01) [Conjunto de datos]. Zenodo. https://doi.org/10.5281/zenodo.8286529
- Laizer, H., & Mduma, N. (2025). Irish potato imagery dataset for detection of early and late blight diseases. *Data in Brief, 60*, 111549. https://doi.org/10.1016/j.dib.2025.111549
- NASA. (s. f.). *POWER | Prediction Of Worldwide Energy Resources* [Conjunto de datos]. NASA Langley Research Center. https://power.larc.nasa.gov/

---

## Anexo A - Prueba de acoplamiento

Clave: **(región, mes)** — región ∈ {Mbeya, Iringa, Njombe, Songwe}; mes ∈ {2022-11 … 2023-04}.

Cada fila une un dato de la rama de imagen (nº de imágenes de ese bloque de recolección, o una imagen de muestra) con el clima de NASA POWER para esa región y mes. **Los valores de la serie se llenan ejecutando la consulta de abajo** (no se inventan).

| N.º | Clave (región, mes) | Dato de la rama de imagen (archivo o rasgo) | Dato de la serie (variable y valor) |
| --- | --- | --- | --- |
| 1 | Mbeya, 2022-11 | *(p. ej., lateblt/IMG_xxxx.jpg)* | RH2M = _(…)_ %, T2M = _(…)_ °C |
| 2 | Mbeya, 2022-12 | | RH2M = _(…)_, T2M = _(…)_ |
| 3 | Mbeya, 2023-01 | | |
| 4 | Iringa, 2022-12 | | |
| 5 | Iringa, 2023-01 | | |
| 6 | Iringa, 2023-02 | | |
| 7 | Njombe, 2023-01 | | |
| 8 | Njombe, 2023-02 | | |
| 9 | Songwe, 2023-02 | | |
| 10 | Songwe, 2023-03 | | |

Código o consulta que produjo las filas (rama temporal, NASA POWER; se ajustan lat/lon por región):

```python
import requests, pandas as pd

# Coordenadas aproximadas por región (Tierras Altas del Sur de Tanzania)
regiones = {
    "Mbeya":  (-8.90, 33.46),
    "Iringa": (-7.77, 35.69),
    "Njombe": (-9.34, 34.77),
    "Songwe": (-9.00, 33.00),
}
params = "T2M,RH2M,PRECTOTCORR"
filas = []
for region, (lat, lon) in regiones.items():
    url = ("https://power.larc.nasa.gov/api/temporal/monthly/point"
           f"?parameters={params}&community=AG&latitude={lat}&longitude={lon}"
           "&start=2022&end=2023&format=JSON")
    r = requests.get(url, timeout=60).json()
    p = r["properties"]["parameter"]
    for ym in ["202211","202212","202301","202302","202303","202304"]:
        filas.append({
            "region": region, "mes": ym,
            "T2M": p["T2M"].get(ym), "RH2M": p["RH2M"].get(ym),
            "PRECTOTCORR": p["PRECTOTCORR"].get(ym),
        })
print(pd.DataFrame(filas))   # se toman 10 filas reales para el anexo
```

## Anexo B - Evidencias del test de procedencia

1. **Cadena de procedencia** (un archivo por fila):

| Archivo (nombre exacto) | URL o DOI del productor primario | Fecha de descarga | Huella SHA-256 |
| --- | --- | --- | --- |
| healthy.zip | https://doi.org/10.5281/zenodo.8286529 | _(AAAA-MM-DD)_ | _(correr hashlib)_ |
| earlyblt.zip | https://doi.org/10.5281/zenodo.8286529 | _(AAAA-MM-DD)_ | _(correr hashlib)_ |
| lateblt.zip | https://doi.org/10.5281/zenodo.8286529 | _(AAAA-MM-DD)_ | _(correr hashlib)_ |

Código de la huella: `hashlib.sha256(open(ruta, "rb").read()).hexdigest()`

2. **Descarga trazable:** la celda de carga descarga los tres .zip desde el DOI de Zenodo (o una copia con la misma huella). Búsqueda en el cuaderno: `grep -inE "kaggle|kagglehub|/kaggle/input" *.ipynb` → sin coincidencias.

3. **Búsqueda declarada de espejos** (fecha 2026-10-30): se buscó «Irish Potato Imagery Dataset» y los nombres de archivo en kaggle.com/datasets. Coincidencias a declarar tras la búsqueda del estudiante; el espejo conocido es **Hugging Face `Project-AgML/potato_leaf_blight`**, con el **mismo origen Zenodo** (no es un origen Kaggle). El corpus PlantVillage de papa (muy presente en Kaggle) es **distinto** (imágenes de laboratorio, fondo controlado): se contrasta en el punto 5.

4. **Huella de crudeza** (antes de limpiar): filas × columnas = **58.709 imágenes** en 3 clases - faltantes: a reportar tras cargar - balance de la etiqueta = sana 20.438 / *early* 17.772 / *late* 20.499 (≈ 35 % / 30 % / 35 %), binario 34,8 % sana / 65,2 % enferma.

5. **Contraste con el espejo** (PlantVillage papa): huella SHA-256 distinta, imágenes de campo (no de laboratorio), fondos y conteos distintos, columnas/estructura originales de Zenodo. Se adjunta una imagen de muestra de cada fuente para evidenciar la diferencia.

## Anexo C - Checklist de protección de datos personales (una copia por fuente)

**Fuente: Irish Potato Imagery Dataset (Zenodo 8286529)**

Regla de la Fase 1: sin personas identificables. Solo se usan datos públicos, agregados o anonimizados por la fuente oficial. «Ley» = Ley 1581 de 2012; «DUR» = Decreto 1074 de 2015.

**Resultado** (se marca uno):
- [x] Sin datos de personas.
- [ ] Datos de personas anonimizados por la fuente.
- [ ] Datos personales o sensibles → no admisibles en la Fase 1.

### A. ¿Hay datos personales? (Ley, art. 3 lit. c)
- [x] Se revisaron columnas, imágenes y metadatos: el contenido son hojas de papa, sin identificadores directos (nombre, documento, rostro, etc.).
- [x] Identificadores indirectos: **riesgo de EXIF/GPS** en fotos de smartphone → se **borran los metadatos EXIF/GPS** antes de cualquier carga a Colab/Drive, y la ubicación se mantiene a nivel de región.
- [x] No hay identificadores seudonimizados.

### B. ¿Hay datos sensibles? (Ley, art. 5)
- [x] No hay datos de salud humana, biométricos ni sensibles: es fitosanidad vegetal.

### C. ¿Hay niños, niñas o adolescentes? (Ley, art. 7)
- [x] No aplica: no hay personas.

### D. Base legal o autorización para datos de terceros
- [x] Fuente pública oficial (Zenodo, con DOI y licencia citable); se citan sus términos de uso una vez confirmada la licencia.

### E. Finalidad (Ley, art. 4 lit. b)
- [x] «Uso académico para entrenar y evaluar un modelo en el curso; no se toman decisiones sobre personas identificadas».

### F. Anonimización y riesgo de reidentificación
- [x] No hay identificadores directos; se borran los EXIF/GPS de las imágenes.
- [x] Prueba de reidentificación: no es posible identificar a una persona con hojas de papa.

### G. Licencia de uso (verificada en la fuente primaria)
- [ ] **Pendiente:** anotar nombre y versión de la licencia leída en la ficha de Zenodo del DOI, con el enlace, y las obligaciones (atribución, etc.).

### H. Transferencia internacional (Colab, Drive, GitHub, asistentes de IA)
- [x] A Colab/Drive/GitHub solo se suben datos sin personas identificables (hojas de papa).
- [x] A los asistentes de IA no se les pegan registros reales de personas (no los hay).

### I. Minimización y conservación
- [x] Solo se conservan las imágenes y columnas necesarias; se declara dónde se guardan los crudos y que se borran al terminar la Fase 3.

### J. Publicación del repositorio (Ley, art. 4 lit. f)
- [x] El repositorio es privado y compartido con el docente, o público con un script que descarga desde Zenodo (datos en `.gitignore` si la licencia no permite redistribuir); las salidas no muestran datos personales.

---

**Fuente: NASA POWER** — Resultado: **Sin datos de personas** (datos meteorológicos agregados por celda geográfica). Licencia: datos NASA de libre uso, con la atribución indicada. Transferencia internacional: solo datos ambientales, sin personas. Las demás casillas (A–J) se marcan «no aplica / sin personas».

**Declaración.** Lo consignado en este checklist es verdadero y se revisó para cada fuente de la Propuesta.

| Integrante | Firma | Fecha (AAAA-MM-DD) |
| --- | --- | --- |
| Juan Guillermo Montaño Junca | | 2026-10-30 |
| Jair Andrés Valderrama Cano | | 2026-10-30 |
