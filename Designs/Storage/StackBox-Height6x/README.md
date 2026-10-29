# StackBox · altura 6×

Variante de la [StackBox adaptada](../StackBox-105x147x28/), con altura exterior
multiplicada por **6**: **198,68 mm**. La base es de
**114,32 × 156,32 mm**, con la misma tapa y los mismos perfiles de encaje.
Se ha extendido el tramo recto de las paredes, conservando el fondo y el rebaje superior.

![StackBox de altura 6× con su tapa](Preview.png)

## Archivos para imprimir

Para imprimir un pote y su tapa juntos, utiliza los
[proyectos por conjunto, ya laminados](../../../PrintPlates/StackBox-Pote-y-Tapa/).

- [Proyecto 3MF para Bambu Studio, sin AMS](Files/StackBox_Height6x_NoAMS.3mf)
- [STL de la caja](Files/StackBox_Caja_Height6x.stl)
- [STL de la tapa compatible](Files/StackBox_Tapa_Compatible.stl)
- [Sumas SHA-256](Files/SHA256SUMS.txt)

Abre el 3MF como proyecto y vuelve a laminar antes de imprimir. Incluye caja
y tapa en una placa. Si ya tienes una tapa de la versión base, puedes
reutilizarla e imprimir solo la caja.

## Medidas

Orden: **ancho × largo × alto**, en milímetros.

| Elemento | Medidas |
| --- | --- |
| Exterior de la caja | 114,32 × 156,32 × 198,68 |
| Volumen rectangular útil con tapa cerrada | 105,40 × 147,40 × 193,97 |
| Exterior de la tapa | 114,32 × 156,32 × 8,00 |
| Factor aplicado a la altura exterior | 6× sobre 33,113126412 mm |

La cavidad conserva sus esquinas redondeadas y la holgura horizontal de la
adaptación base. La receta completa está en [Derivation.json](Derivation.json).

## Configuración y validación

- Bambu Lab A1, boquilla de 0,4 mm, placa de 256 × 256 mm.
- PLA Basic, capas de 0,28 mm, 2 paredes, relleno grid del 15 %, sin soportes.
- [Registro del perfil conservado](../../../Profiles/Process/StackBox-A1-0.28mm.snapshot.json).
- Mallas cerradas y orientadas; geometría de la tapa idéntica a la base.
- Fondo y borde superior conservados, con comprobación de cierre y espacio útil.
- Ambas piezas caben en el volumen configurado de la A1.
- Laminado completado en Bambu Studio: **10h 40m 1s**, **710 capas**.
- Estado de la prueba física: **pendiente**.

El tiempo corresponde a caja y tapa con el perfil archivado. Los resultados
están en [Verification.json](Verification.json).

## Reproducir la variante

Desde la raíz del repositorio, con Python 3.10 o posterior:

```sh
python Scripts/Extend-StackBox.py --factor 6 --output-dir LocalExports/StackBox-Height6x
```

El script genera las mallas y el proyecto sin renders. Los archivos publicados
incluyen vistas previas propias sin texto.

## Créditos

Diseño original de **Agro1223**; adaptación y variante archivadas por **iiroak**.
Consulta [Attribution.md](Attribution.md) para el origen y el permiso de publicación.
