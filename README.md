# BambuLabA1-Archive

Mi archivo personal de diseños 3D, modificaciones, perfiles de impresión,
configuraciones y pruebas con la **Bambu Lab A1**. Lo guardo aquí para tenerlo
ordenado y compartir lo que pueda servirle a alguien más.

## Diseños

| Diseño | Descripción | Archivos | Estado |
| --- | --- | --- | --- |
| [StackBox · 105 × 147 × 28 mm](Designs/StackBox-105x147x28/) | Caja y tapa adaptadas para un objeto de esas medidas, con pequeña holgura | [3MF](Designs/StackBox-105x147x28/Files/StackBox_105x147x28mm_Holgura_NoAMS.3mf), [STL caja](Designs/StackBox-105x147x28/Files/StackBox_Caja_105x147x28mm.stl), [STL tapa](Designs/StackBox-105x147x28/Files/StackBox_Tapa_105x147x28mm.stl) | Verificación digital y laminado; pendiente de prueba física |
| [StackBox · altura 3×](Designs/StackBox-Height3x/) | Misma base y tapa; caja de 99,34 mm de alto exterior | [3MF](Designs/StackBox-Height3x/Files/StackBox_Height3x_NoAMS.3mf), [STL caja](Designs/StackBox-Height3x/Files/StackBox_Caja_Height3x.stl) | Verificación digital y laminado; pendiente de prueba física |
| [StackBox · altura 6×](Designs/StackBox-Height6x/) | Misma base y tapa; caja de 198,68 mm de alto exterior | [3MF](Designs/StackBox-Height6x/Files/StackBox_Height6x_NoAMS.3mf), [STL caja](Designs/StackBox-Height6x/Files/StackBox_Caja_Height6x.stl) | Verificación digital y laminado; pendiente de prueba física |

![StackBox ajustada: caja y tapa](Designs/StackBox-105x147x28/Preview.png)

## Placas listas para la A1

[Un pote con su tapa por proyecto: versiones 3× y 6×](PrintPlates/StackBox-Pote-y-Tapa/).
Incluye los archivos ya laminados para **A1, boquilla de 0,4 mm, PLA Basic y PEI texturizado**,
además de los proyectos editables.

## Organización

```text
Designs/       Un directorio por diseño: archivos, medidas, vista previa y créditos
PrintPlates/   Proyectos agrupados y archivos ya laminados para imprimir
Profiles/      Ajustes de proceso, filamento e impresora
Scripts/       Herramientas para generar o modificar archivos
Docs/          Convenciones y registro de pruebas
Templates/     Plantillas para añadir nuevos diseños
```

- Cada diseño tiene su propia ficha y atribución.
- Las medidas se registran en milímetros; se distingue espacio interior de tamaño exterior.
- Los proyectos 3MF conservan el perfil utilizado. Los JSON marcados como snapshot son registros de ajustes, no presets importables.
- [Cómo añadir contenido](Docs/Conventions.md) · [Registro de impresiones](Docs/Print-Log.md)

## Licencias

El código y la documentación originales de este archivo se publican bajo
[MIT](LICENSE). Los diseños derivados y recursos de terceros conservan la
licencia y los permisos indicados en su ficha; no pasan automáticamente a MIT.
Consulta [el alcance de las licencias](LICENSES.md) y los
[créditos de StackBox](Designs/StackBox-105x147x28/Attribution.md).
