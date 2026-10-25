# Scripts

## Resize-StackBox.py

Aplica la receta archivada al 3MF original y genera un 3MF y dos STL. Requiere
Python 3.10 o posterior, sin paquetes adicionales.

```sh
python Scripts/Resize-StackBox.py --help
python Scripts/Resize-StackBox.py /ruta/StackBox_V3_NoAMS_Optimal.3mf --output-dir LocalExports/StackBox
```

El original debe obtenerse por separado. Se verifica su SHA-256 y se evita
sobrescribir carpetas de salida existentes. Los archivos generados conservan
la atribución y licencia del modelo base.

## Extend-StackBox.py

Crea variantes más altas a partir del 3MF base ya incluido en este repositorio.
El factor multiplica la **altura exterior de la caja**. La planta, el fondo,
el rebaje superior y la tapa conservan sus dimensiones; se extiende el tramo
recto de las paredes. Requiere Python 3.10 o posterior, sin paquetes adicionales.

```sh
python Scripts/Extend-StackBox.py --factor 3 --output-dir LocalExports/StackBox-Height3x
python Scripts/Extend-StackBox.py --factor 6 --output-dir LocalExports/StackBox-Height6x
```

La carpeta de salida debe ser nueva. Se generan el 3MF, los STL y
`Derivation.json`, que registra las medidas y la transformación. El script
descarta las imágenes antiguas; los proyectos publicados incluyen renders
propios de cada altura. El resultado debe caber dentro de la altura de la
impresora configurada en el proyecto.
