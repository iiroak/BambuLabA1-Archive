# Cómo organizar contenido nuevo

1. Crea `Designs/Nombre-Del-Diseno/` y copia la plantilla de ficha.
2. Guarda los 3MF y STL finales en `Files/`, y una vista previa junto al README.
3. Registra medidas interiores y exteriores por separado, siempre en milímetros.
4. Incluye el origen, autor, licencia y permiso de redistribución de cada modelo derivado.
5. Vincula los ajustes de proceso, material e impresora usados en `Profiles/`.
6. Indica si el diseño está solo verificado digitalmente o también impreso.

Para los directorios se usa PascalCase con guiones: `StackBox-105x147x28`.
Los nombres deben ser estables; las variantes se distinguen por medidas o uso.
Los cambios posteriores quedan en el historial de Git.

`LocalExports/` y `Work/` están ignorados para pruebas y archivos temporales.
Las contraseñas, códigos de acceso y configuraciones globales de la aplicación
no forman parte del repositorio.
