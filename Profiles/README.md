# Perfiles y configuraciones

- [Process](Process/): altura de capa, paredes, velocidades y relleno.
- [Filament](Filament/): ajustes de materiales y temperaturas.
- [Printer](Printer/): referencia de impresora y boquilla.

Los archivos terminados en `.snapshot.json` son registros legibles de ajustes,
no presets nativos importables. Para recuperar la configuración completa de
StackBox, abre su 3MF como proyecto en Bambu Studio.

Al añadir un preset nativo, conserva `inherits`, su versión y el modelo de
impresora compatible. Guarda aquí exportaciones de perfiles; la configuración
global de la aplicación y los códigos de acceso quedan fuera del archivo.
