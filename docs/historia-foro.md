Buenas noches, profe y compañeros.

Les compartimos nuestra propuesta (Juan Guillermo Montaño y Jair Andrés Valderrama). El repo está en https://github.com/N3UR0SlS/Centinela-Papa y la Propuesta de Datos completa va adjunta en PDF, también dentro de la carpeta propuesta/.

Nuestro Centinela busca anticipar si una hoja de papa tiene tizón (sí o no), para que un servicio de extensión agrícola focalice el control antes de perder el lote. Trabajamos dos modalidades reales: las fotos de hoja tomadas en campo (58.709 imágenes de Zenodo, en sana, tizón temprano y tizón tardío) y el clima diario de NASA POWER para esa misma región y periodo. En la Fase 1 aplanamos la imagen para el MLP; más adelante entran la CNN, la serie con una LSTM y la fusión, y en la Fase 3 la rama visual corre offline en una tablet con LiteRT.

Las dos fuentes se acoplan de forma agregada por región y mes, con la salvedad de que una foto no trae su propio registro climático; la clave y la consulta que genera las 10 filas quedan en el anexo A. Sobre procedencia, el tema de papa abunda en Kaggle vía PlantVillage, pero es un corpus distinto (de laboratorio): lo declaramos y contrastamos en el anexo B, y no bajamos nada de Kaggle. Y como son hojas, no hay datos de personas: borramos los EXIF/GPS y dejamos los datos locales, reproducibles con un script desde la fuente.

Cualquier comentario para afinarlo nos sirve bastante. Gracias.
