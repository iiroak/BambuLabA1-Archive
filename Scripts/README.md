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
