# Perfiles de filamento Bambu Lab A1 - Version 02.08.00.05

**20 JSON incluidos (18 recomendados + 2 ejemplos de compatibilidad BLOQUEADOS).**

- 5 familias: Creality CR-PETG, eSUN PETG estandar, ELEGOO PLA+ estandar, ELEGOO PLA Marmol, ELEGOO PLA Bronce-Cobre.
- 4 diametros en cada familia: 0.2 / 0.4 / 0.6 / 0.8 mm.
- Cada archivo contiene `"version": "02.08.00.05"` y `"compatible_printers"` para la Bambu Lab A1.
- Para boquillas 0.2 de los materiales abrasivos, los 2 JSON van en ADVERTENCIA_NO_USAR_ABRASIVOS_0_2/ y tienen `compatible_printers: []`, para que no se activen en una A1. Son referencias, NO IMPORTAR para imprimir.
- Se usan boquillas de acero endurecido para PLA Marmol y Bronce-Cobre; para PLA Marmol ELEGOO recomienda >=0.4 mm.
- El perfil Creality de 0.4 mm mantiene los 255 C primera capa / 250 C resto / 80 C cama / 0.95 flujo / 10 mm3/s / ventilacion 25-60% del ZIP aportado.
- Las variantes 0.6 y 0.8 de Creality conservan ese caudal de 10 mm3/s por prudencia, hasta calibrarlas.
- Los perfiles son de FILAMENTO, no modifican el perfil de PROCESO (altura de capa, paredes, velocidad de movimientos) ni el G-code de la maquina.
- `version` esta incluida porque lo solicitas, pero no garantiza que todas las versiones de Bambu Studio acepten por si solas el JSON; la herencia y los perfiles instalados deben coincidir.

## Importacion

1. Bambu Studio -> Archivo -> Importar -> Importar configuraciones.
2. Seleccionar SOLO los JSON recomendados de la carpeta de la boquilla que tengas instalada.
3. Seleccionar en la impresora el diametro de boquilla que realmente este instalado.
4. Configurar la placa correspondiente (se optimizo para Textured PEI); no reutilizar ajustes de cama para placas incompatibles.
5. Hacer prueba pequena y calibracion de flujo (Flow Ratio) y flujo dinamico/K por bobina si hace falta. Evitar Sport/Ludicrous hasta validar.

## Temperaturas y caudal por familia

| Familia | Boquilla inicial/resto | Cama PEI inicial/resto | Ratio inicial | Max vol 0.2/0.4/0.6/0.8 mm3/s |
|---|---|---|---|---|
| Creality CR-PETG | 255 / 250 C | 80 / 80 C | 0.95 | 1 / 10 / 10 / 10 |
| eSUN PETG | 250 / 245 C | 80 / 80 C | 0.95 | 1 / 10 / 10 / 13 |
| ELEGOO PLA+ | 215 / 215 C | 60 / 55 C | 0.98 | 1.6 / 7 / 9 / 10 |
| ELEGOO PLA Marmol | 215 / 210 C | 60 / 55 C | 0.98 | NO USAR / 6 / 8 / 10 |
| ELEGOO PLA Bronce-Cobre | 215 / 210 C | 60 / 55 C | 0.98 | NO USAR / 5.5 / 8 / 10 |

**Notas**
- Estos parametros son puntos de partida basados en fuentes y en tu perfil validado Creality. Fuera del Creality de 0.4, no estan calibrados fisicamente con tus bobinas.
- PLA+ Madera corresponde a color madera, NO PLA Wood con carga real. Si la etiqueta dice PLA Wood real, se necesita un perfil distinto.
- No incluir automaticamente otros materiales por compartir marca o color. PETG Matte/HS, PLA Silk o PLA-CF requieren otra familia.
- No se fija manualmente el factor K.

## Referencias
- https://github.com/bambulab/BambuStudio/blob/master/resources/profiles/BBL/filament/Generic%20PLA%20%40BBL%20A1%200.2%20nozzle.json
- https://github.com/bambulab/BambuStudio/blob/master/resources/profiles/BBL/filament/Generic%20PETG%20%40BBL%20A1%200.2%20nozzle.json
- https://github.com/bambulab/BambuStudio/blob/master/resources/profiles/BBL/filament/Generic%20PETG%20%40BBL%20A1.json
- https://www.elegoo.com/en-gb/products/pla-filament-1-75mm-colored-1kg
- https://eu.elegoo.com/products/pla-marble
- https://www.esun3d.com/wiki/petg-basic-vs-petg-vs-petg-pro
- https://www.todotoner.cl/impresoras/impresoras-3d/filamentos/pla-mas-elegoo-madera-1kg
- https://www.todotoner.cl/impresoras/impresoras-3d/filamentos/pla-elegoo-bronce-con-polvo-cobre-1000g
