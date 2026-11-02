# Datos derivados

`rasgos_papa.csv`: rasgos de color y textura por foto, extraídos con `notebooks/extraer_rasgos.py` a partir del Irish Potato Imagery Dataset (Laizer et al., 2023, Zenodo, https://doi.org/10.5281/zenodo.8286529, licencia CC BY 4.0). Es un derivado: no contiene las imágenes ni coordenadas GPS, solo los rasgos, la clase, la fecha de la toma y si la foto tenía GPS (sí/no).

`auditoria_extraccion.json`: conteo por zip de entradas, archivos que no son imagen (`__MACOSX`), fotos procesadas y errores.
