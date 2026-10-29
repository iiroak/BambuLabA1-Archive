# Cómo organizar contenido nuevo

1. Elige una categoría en `Designs/` y crea el directorio del proyecto. Copia la plantilla de ficha.
2. Guarda los 3MF y STL finales en `Files/`, y una vista previa junto al README.
3. Registra medidas interiores y exteriores por separado, siempre en milímetros.
4. Incluye el origen, autor, licencia y permiso de redistribución de cada modelo derivado.
5. Vincula los ajustes de proceso, material e impresora usados en `Profiles/`.
6. Indica si el diseño está solo verificado digitalmente o también impreso.

Para los directorios se usa PascalCase con guiones: `StackBox-105x147x28`.
Los nombres deben ser estables; las variantes se distinguen por medidas o uso.
Los cambios posteriores quedan en el historial de Git.

## Categorías

- `Designs/Storage/`: cajas, tapas, recipientes y organizadores.
- `Designs/A1-Modifications/Cable-Chains/`: guías y soportes de cables de la impresora.
- `Designs/A1-Modifications/AMS-Lite/`: conectores y refuerzos del AMS Lite.
- `Designs/A1-Modifications/Tools/`: accesorios de mantenimiento y herramientas.

Los nombres originales de archivos aportados se conservan en `Files/` para
poder reconocerlos. Cuando una pieza se sustituye, la versión activa queda
en `Files/` y el original anterior se identifica en `Sources/`, con sus sumas
de comprobación y una nota del cambio.

Actualiza los enlaces relativos y las rutas de los scripts al mover un proyecto
entre categorías. Los proyectos 3MF mantienen sus referencias internas al ZIP.

`LocalExports/` y `Work/` están ignorados para pruebas y archivos temporales.
Las contraseñas, códigos de acceso y configuraciones globales de la aplicación
no forman parte del repositorio.
