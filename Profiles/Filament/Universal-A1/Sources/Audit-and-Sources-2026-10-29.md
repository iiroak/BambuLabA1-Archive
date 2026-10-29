# Auditoría de perfiles · Bambu Lab A1 · 29-10-2026

## Alcance

Este paquete corrige de manera limitada la edición anterior usando referencias comunitarias específicas. **Ningún perfil nuevo fue calibrado con las bobinas de la usuaria**, salvo el CR-PETG 0.4 mm que previamente indicó que imprimía correctamente.

Hay **18 perfiles de uso inicial** y **2 referencias de 0.2 mm para abrasivos que NO DEBEN IMPORTARSE**. Los 20 llevan `"version": "02.08.00.05"`. Son configuraciones de *filamento*; no son perfiles de proceso, ni cambian G-code de máquina.

## Cambios concretos contra el ZIP original

| Material | Diámetros | Anterior | Nuevo | Motivo |
|---|---|---|---|---|
| Creality CR-PETG | 0.2 / 0.4 / 0.6 / 0.8 | — | Sin cambios | 0.4 mm ya probado; fuente comunitaria 255/250, flujo .95 |
| eSUN PETG convencional | 0.8 | 13 mm³/s | 10 mm³/s | 13 era extrapolación no demostrada; prudencia al cambiar boquilla |
| ELEGOO PLA+ convencional | 0.4 | 215 °C; 7 mm³/s | 220 °C; 10 mm³/s | Comunidad A1 publica 220-225; un valor de compromiso, sin calibración |
| ELEGOO PLA+ convencional | 0.6 | 215 °C; 9 mm³/s | 220 °C; 10 mm³/s | Igual; extrapolación conservadora |
| ELEGOO PLA+ convencional | 0.8 | 215 °C | 220 °C | Temperatura comunitaria; caudal permanece 10 |
| ELEGOO PLA Mármol | 0.4 / 0.6 / 0.8 | Fan máximo normal 100 % | Fan máximo normal 80 % | Perfil Bambu PLA Marble A1 utiliza rango 60-80 % |
| ELEGOO PLA Bronce-cobre | 0.4 / 0.6 / 0.8 | — | Sin cambios | No se hallaron perfiles calibrados directamente comparables |

No se alteró la temperatura del PLA+ de 0.2 mm (215 °C), debido al pequeño caudal y a que las experiencias comunitarias citadas no fueron específicas de esta boquilla.

## Parámetros con incertidumbre

- eSUN PETG: la ficha oficial actual usa ventilación 100 % y el perfil adopta 40-85 % para mejorar la adhesión de capas. NO afirmar que este ajuste sea óptimo sin una prueba de resistencia y voladizos.
- PETG eSUN 0.95, PLA+ 0.98 y mármol 0.98: ratios de partida, no resultado de calibración física.
- PLA+ a 10 mm³/s en 0.4, 0.6 y 0.8: límite conservador de partida, no máxima capacidad demostrada.
- PLA Mármol y Bronce-cobre: boquilla endurecida >=0.4; preferir 0.6 en impresiones prolongadas si hay atascos. Evitar 0.2.
- La presencia de `version` y JSON sintácticamente correcto NO confirma importación efectiva en una instalación de Bambu Studio. Validar seleccionando el perfil, diámetro y placa Textured PEI antes de imprimir.
- La ventilación de voladizos (hasta 100 %) es distinta de ventilación normal (máximo 80 % en Marble).

## Referencias directas

- Creality community: https://forum.bambulab.com/t/struggling-with-petg-print/180166
- eSUN ficha actual: https://www.esun3d.com/petg-product
- eSUN comunidad A1: https://www.reddit.com/r/BambuLab/comments/1dy3mxo/whats_your_max_volumetric_speed_for_petg/
- ELEGOO PLA+ comunidad: https://www.reddit.com/r/BambuLab/comments/1e0jxj3/elegoo_pla_that_bad/
- ELEGOO PLA+ torre A1: https://www.reddit.com/r/3Dprinting/comments/1uaod08/temp_tower_help/
- ELEGOO PLA+ distribuidor: https://www.todotoner.cl/impresoras/impresoras-3d/filamentos/pla-mas-elegoo-madera-1kg
- PLA Marmol usuario 215 210: https://www.reddit.com/r/3Dprinting/comments/1ildyqb/after_some_advice_here_and_tweaking_settings/
- PLA Marble Bambu referencia: https://tangled.org/logik.al/Orcaslicer-bambulab-standalone/blob/main/resources/profiles/BBL/filament/Bambu%20PLA%20Marble%20%40BBL%20A1.json
- ELEGOO Marble ficha: https://eu.elegoo.com/products/pla-marble
- ELEGOO bronze confirmacion metal: https://us.elegoo.com/products/pla-filament-copper-filled-10-kg
- Comunidad dudas importacion: https://forum.bambulab.com/t/esun-filament-profiles/250238

## Verificación técnica

Los 20 archivos se analizaron como JSON y están dentro del ZIP. La importación en Bambu Studio y el laminado en A1 no se han probado aquí.
