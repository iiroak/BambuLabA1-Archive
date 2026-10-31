# Scripts

Los diseños de almacenamiento están en `Designs/Storage/`; las mejoras de la
impresora están en `Designs/A1-Modifications/`.

## Verify-Filament-Profiles.py

Comprueba los hashes, metadatos y compatibilidad de los perfiles de
[filamento A1](../Profiles/Filament/Universal-A1/). Puede reconstruir el ZIP de
18 presets importables y comparar sus valores con los instalados en Bambu
Studio. Las dos referencias abrasivas de 0,2 mm quedan excluidas del ZIP.
Python 3.10 o posterior, sin dependencias adicionales.

```sh
python Scripts/Verify-Filament-Profiles.py --bundle
python Scripts/Verify-Filament-Profiles.py --installed --report LocalExports/Filament-Verification.json
```

La auditoría de instalación es de solo lectura y resuelve los perfiles padre.
No exporta la configuración global ni los identificadores de la cuenta.

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

## Prepare-StackBox-Plates.py

Prepara un proyecto con los recipientes 3× y 6×, y otro con dos tapas.
Las piezas se giran 90° para colocarlas lado a lado en la A1, con 8 mm de separación.

```sh
python Scripts/Prepare-StackBox-Plates.py --output-dir LocalExports/StackBox-PrintPlates
```

Python 3.10 o posterior, sin paquetes adicionales. La carpeta de salida debe
ser nueva. El script genera proyectos editables y `Layout.json`; los
[archivos publicados](../PrintPlates/StackBox-Height3x-Height6x/) incluyen también
los renders y el G-code ya laminado para A1 / 0,4 mm / PLA Basic / PEI texturizado.
