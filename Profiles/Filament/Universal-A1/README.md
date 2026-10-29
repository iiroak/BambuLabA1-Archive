# Familias de filamento para Bambu Lab A1

18 presets importables para cinco familias, organizados por boquilla. Los nombres
representan formulaciones; el color se elige en el proyecto o en el AMS Lite.

| Familia | 0,2 mm | 0,4 mm | 0,6 mm | 0,8 mm |
| --- | ---: | ---: | ---: | ---: |
| Creality CR-PETG convencional | 1 | 10 | 10 | 10 |
| eSUN PETG convencional | 1 | 10 | 10 | 13 |
| ELEGOO PLA+ convencional | 1,6 | 7 | 9 | 10 |
| ELEGOO PLA Mármol Mineral | — | 6 | 8 | 10 |
| ELEGOO PLA Bronce-Cobre | — | 5,5 | 8 | 10 |

Los números son límites volumétricos iniciales en mm³/s, tomados del paquete
recibido el 29 de octubre de 2026. La instalación y la herencia se verifican por
software. La calibración de temperatura, flujo y dinámica/K corresponde a cada
bobina y combinación de boquilla; esta incorporación no añade pruebas físicas.

## Archivos e instalación

- [Boquilla de 0,2 mm](Nozzle-0.2/): tres familias sin cargas.
- [Boquilla de 0,4 mm](Nozzle-0.4/): cinco familias.
- [Boquilla de 0,6 mm](Nozzle-0.6/): cinco familias.
- [Boquilla de 0,8 mm](Nozzle-0.8/): cinco familias.
- [ZIP de instalación con los 18 presets](Bambu-A1-Universal-Filaments-18.zip).
- [Manifiesto y SHA-256 de los 20 originales](Manifest.json).
- [Verificación de la instalación](Verification.json).

En Bambu Studio, usa **Archivo → Importar → Importar configuraciones** y elige
el ZIP o los JSON correspondientes. Selecciona después el diámetro instalado en
la impresora; el selector de filamentos filtra las variantes por esa boquilla.

Los archivos conservan `version: "02.08.00.05"`, su preset `inherits`, el nombre y
los ajustes recibidos. La marca y el diámetro no sustituyen la identificación de
la línea de material: PETG HS, PLA Silk, PLA-CF o PLA con fibras de madera reales
requieren su familia correspondiente. El PLA+ de color madera pertenece a esta
familia solo cuando la etiqueta confirma que es PLA+ convencional.

## Referencias de abrasivos de 0,2 mm

Los dos archivos recibidos para Mármol y Bronce-Cobre de 0,2 mm se conservan en
[Reference-Only-Nozzle-0.2](Reference-Only-Nozzle-0.2/) con extensión
**`.json.disabled`** y quedan fuera del ZIP y de la instalación.

La documentación original llamaba bloqueo a `compatible_printers: []`. Una lista
vacía no impone por sí sola esa restricción en Bambu Studio. Por eso se evita
ofrecer estas referencias como presets importables. Sus bytes y hashes originales
se conservan para trazabilidad. Las notas recibidas requieren boquilla endurecida
para los materiales con cargas; consulta también la ficha de la bobina real.

## Comprobación y mantenimiento

Desde la raíz del repositorio, con Python 3.10 o posterior:

```sh
python Scripts/Verify-Filament-Profiles.py --bundle
python Scripts/Verify-Filament-Profiles.py --installed --report LocalExports/Filament-Verification.json
```

El script comprueba hashes, nombres, versión, compatibilidad por diámetro y el
contenido del ZIP. Con `--installed` compara los valores efectivos con el almacén
de usuario de Bambu Studio, resolviendo la herencia y equivalencias numéricas
como `0.40` y `0.4`. No modifica los presets instalados ni exporta códigos de
acceso. `--install-dir` y `--user-data-dir` permiten indicar otras ubicaciones.

El Creality de 0,4 mm conserva 255/250 °C, PEI a 80 °C, flujo 0,95 y ventilación
25–60 % del perfil previo aportado. Los perfiles anteriores con nombres distintos
permanecen disponibles en Bambu Studio.

## Procedencia

El paquete fue aportado por el mantenedor. Se guardan las
[notas originales](Sources/Original-Notes.md) y su
[manifiesto original](Sources/Original-Manifest.json). Los presets de Bambu Lab
referenciados por `inherits` se obtienen de Bambu Studio y conservan su atribución.
Las notas de origen contienen las fuentes usadas para proponer los parámetros;
esta incorporación valida los archivos y la instalación, sin certificar esas
propuestas como calibraciones medidas.
