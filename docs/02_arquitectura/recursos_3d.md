# Recursos GLB de la galería

Los originales fueron aportados por el usuario y se localizaron en `recursos_3d/referencias/modelos/`. La fecha exacta de descarga no está registrada. El 25 de noviembre de 2026 se verificaron sus licencias y se copiaron, sin cambios binarios, a `instrumentos/static/instrumentos/modelos/`. Las páginas de origen y los metadatos GLB identifican a Innerscene Corp y declaran [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/).

| Archivo y fuente | Bytes | Nodos / mallas / triángulos | Materiales / PNG | Dimensiones XYZ de la escena, en metros | Acabado |
| --- | ---: | --- | --- | --- | --- |
| [solid-body-electric-guitar.glb](https://www.innerscene.com/tools/library/3d-parts/solid-body-electric-guitar-76088e09) | 1.156.544 | 108 / 107 / 32.596 | 5 / 5 | 0,330 × 1,010 × 0,093 | Cuerpo tallado, material `red`. |
| [four-string-bass-guitar.glb](https://www.innerscene.com/tools/library/3d-parts/four-string-bass-guitar-f9714b96) | 1.028.076 | 90 / 89 / 28.012 | 5 / 5 | 0,350 × 1,159 × 0,093 | Cuerpo tallado, material `blue`. |
| [88-key-keyboard-instrument.glb](https://www.innerscene.com/tools/library/3d-parts/88-key-keyboard-instrument-4c990660) | 1.702.284 | 129 / 128 / 32.320 | 5 / 5 | 1,326 × 0,170 × 0,304 | Carcasa inferior y dos tapas laterales, material `black`. Las teclas y controles conservan su material. |
| [five-piece-drum-kit.glb](https://www.innerscene.com/tools/library/3d-parts/five-piece-drum-kit-daff10f4) | 3.361.348 | 323 / 322 / 109.088 | 9 / 9 | 1,814 × 1,239 × 1,618 | Cuatro cascos con material `blue`. La caja de acero mantiene su acabado, igual que los platillos, parches y herrajes. |

Los cuatro son GLB 2.0 con eje Y vertical, texturas PNG incrustadas y sin extensiones obligatorias. Khronos glTF Validator 2.0.0-dev.3.10 devolvió cero errores, advertencias e informes en cada archivo. GLTFLoader leyó las cuatro escenas y sus materiales. La batería es una representación acústica de la categoría.

## SHA-256 de las copias y originales

```text
91878d0e616c4dbbfa4bbeb7abbe9caf9a0f6d3c779cfe944a7fead7d84ad148  solid-body-electric-guitar.glb
c65083c807957c2e73f065d9c8c4881565e09e30a7f51ee217747321c841b7bf  four-string-bass-guitar.glb
fe338132bda7e7eb6e05a8f87bed8ca791051645effa7b1ba40069cad4fbf362  88-key-keyboard-instrument.glb
b395c512cc4de3c0a65d7564bbc12db823b4c3c2c1b17958178f316f7f9ff1f8  five-piece-drum-kit.glb
```

## Dependencia local

Three.js **0.180.0** incluye el cargador glTF y un renderizador WebGL 2 con materiales PBR. La galería utiliza el paquete oficial `three@0.180.0` y sirve localmente los módulos de construcción, GLTFLoader, BufferGeometryUtils y RoomEnvironment, junto a su licencia MIT. Los únicos cambios a los módulos del paquete fueron usar extensión `.mjs` y ajustar sus importaciones relativas. El cliente solicita solo el GLB de la sala activa. [Código fuente de Three.js r180](https://github.com/mrdoob/three.js/tree/r180) · [Licencia incluida](../../instrumentos/static/instrumentos/vendor/three-0.180.0/LICENSE.txt)
