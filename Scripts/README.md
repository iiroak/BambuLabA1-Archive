# Scripts

Los diseños de almacenamiento están en `Designs/Storage/`; las mejoras de la
impresora están en `Designs/A1-Modifications/`.

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

## Update-Bed-Mount-2026.py

Usa el **archivo suelto plano 2026** para sustituir el soporte antiguo dentro
del **conjunto completo RV01**. Conserva los otros objetos, sus posiciones y
el perfil del conjunto. Python 3.10 o posterior, sin paquetes adicionales.

```sh
python Scripts/Update-Bed-Mount-2026.py "Designs/A1-Modifications/Cable-Chains/Bed-Dragchain-2026/Sources/obj_42+bed+mount_Provided2026.3mf" "Designs/A1-Modifications/Cable-Chains/Bed-Dragchain-2026/Sources/A1+bed+dragchain+RV01_Original.3mf" --output LocalExports/Bed-Dragchain-Flat-2026.3mf
```

La salida debe ser nueva. El primer argumento es la pieza plana y el segundo
el conjunto original. El script rechaza el orden inverso y registra el cambio
en `.replacement.json`.
