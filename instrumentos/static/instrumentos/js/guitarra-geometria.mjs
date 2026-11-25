// Prototipo original. Cada vértice guarda posición, normal, material y acabado.
export function geometriaGuitarra(bajo = false) {
    const vertices = [];
    const cuerdas = bajo ? 4 : 6;
    const espacioCuerdas = bajo ? .035 : .024;
    const madera = [.64, .40, .19];
    const diapasón = [.17, .095, .058];
    const metal = [.82, .79, .70];
    const negro = [.12, .11, .10];
    const crema = [.87, .79, .63];
    const blanco = [1, 1, 1];

    function triangulo(a, b, c, normal, color, acabado) {
        for (const punto of [a, b, c]) vertices.push(...punto, ...normal, ...color, acabado);
    }

    function cara(a, b, c, d, normal, color, acabado) {
        triangulo(a, b, c, normal, color, acabado);
        triangulo(a, c, d, normal, color, acabado);
    }

    function extruir(contorno, [cx, cy], fondo, frente, color, acabado = 0) {
        for (const [indice, [x, y]] of contorno.entries()) {
            const [nx, ny] = contorno[(indice + 1) % contorno.length];
            const a = [x, y, frente], b = [nx, ny, frente];
            const c = [nx, ny, fondo], d = [x, y, fondo];
            const longitud = Math.hypot(nx - x, ny - y);
            triangulo([cx, cy, frente], a, b, [0, 0, 1], color, acabado);
            triangulo([cx, cy, fondo], c, d, [0, 0, -1], color, acabado);
            cara(a, d, c, b, [(ny - y) / longitud, (x - nx) / longitud, 0], color, acabado);
        }
    }

    function caja(x, y, z, ancho, alto, grosor, color) {
        const izquierda = x - ancho / 2, derecha = x + ancho / 2;
        const abajo = y - alto / 2, arriba = y + alto / 2;
        extruir([[izquierda, abajo], [derecha, abajo], [derecha, arriba], [izquierda, arriba]],
            [x, y], z - grosor / 2, z + grosor / 2, color);
    }

    function disco(x, y, radio, fondo, frente, color) {
        const contorno = Array.from({length: 16}, (_, i) => {
            const angulo = i * Math.PI / 8;
            return [x + radio * Math.cos(angulo), y + radio * Math.sin(angulo)];
        });
        extruir(contorno, [x, y], fondo, frente, color);
    }

    // La interpolación cúbica suaviza la silueta sin perder la forma de los cuernos.
    function suavizar(puntos) {
        const total = puntos.length;
        return puntos.flatMap((b, i) => {
            const a = puntos[(i + total - 1) % total];
            const c = puntos[(i + 1) % total];
            const d = puntos[(i + 2) % total];
            return Array.from({length: 5}, (_, paso) => {
                const t = paso / 5;
                return b.map((v, j) => .5 * (
                    2 * v + (c[j] - a[j]) * t
                    + (2 * a[j] - 5 * v + 4 * c[j] - d[j]) * t ** 2
                    + (-a[j] + 3 * v - 3 * c[j] + d[j]) * t ** 3
                ));
            });
        });
    }

    function tallarCuerpo(contorno) {
        const centroY = -.91;
        const perfil = [[.93, -.136], [1, -.094], [1, .088], [.94, .136]];
        const punto = ([x, y], factor, z) => [x * factor, centroY + (y - centroY) * factor, z];
        for (const [i, a] of contorno.entries()) {
            const b = contorno[(i + 1) % contorno.length];
            const [dx, dy] = [b[0] - a[0], b[1] - a[1]];
            const longitud = Math.hypot(dx, dy);
            const [nx, ny] = [dy / longitud, -dx / longitud];
            for (const [j, pendiente] of [-.75, 0, .75].entries()) {
                const [factor, z] = perfil[j];
                const [siguiente, nz] = perfil[j + 1];
                const magnitud = Math.hypot(1, pendiente);
                cara(punto(a, factor, z), punto(b, factor, z),
                    punto(b, siguiente, nz), punto(a, siguiente, nz),
                    [nx / magnitud, ny / magnitud, pendiente / magnitud], blanco, 1);
            }
            triangulo([0, centroY, perfil[0][1]], punto(b, ...perfil[0]), punto(a, ...perfil[0]),
                [0, 0, -1], blanco, 1);
            triangulo([0, centroY, perfil[3][1]], punto(a, ...perfil[3]), punto(b, ...perfil[3]),
                [0, 0, 1], blanco, 1);
        }
    }

    const cuerpo = [
        [-.17, -1.55], [.16, -1.53], [.40, -1.43], [.54, -1.25], [.58, -1.02],
        [.53, -.84], [.41, -.69], [.36, -.54], [.41, -.33], [.39, -.20],
        [.31, -.17], [.25, -.23], [.18, -.41], [.10, -.46], [-.12, -.45],
        [-.21, -.36], [-.28, -.13], [-.39, -.07], [-.47, -.14], [-.47, -.32],
        [-.42, -.51], [-.43, -.68], [-.55, -.86], [-.59, -1.06], [-.55, -1.27],
        [-.40, -1.46],
    ];
    tallarCuerpo(suavizar(cuerpo));
    extruir(suavizar([[-.23, -1.09], [.25, -1.09], [.36, -.95], [.29, -.76],
        [.24, -.69], [.25, -.47], [.07, -.55], [-.15, -.53], [-.15, -.76]]),
    [.06, -.84], .136, .148, crema);
    const mastil = [[-.11, -.42], [.11, -.42], [.079, 1.14], [-.079, 1.14]];
    extruir(mastil, [0, .36], -.078, .116, madera);
    extruir(mastil, [0, .36], .116, .153, diapasón);
    extruir(suavizar([[-.08, 1.10], [.079, 1.10], [.10, 1.22], [.18, 1.43],
        [.17, 1.54], [.08, 1.61], [-.12, 1.57], [-.153, 1.46], [-.11, 1.20]]),
    [0, 1.35], -.065, .11, madera);
    caja(0, 1.13, .161, .165, .03, .018, crema);

    for (const [indice, y] of [-.57, -.74, -.91].entries()) {
        caja(0, y, .161, .235, .071, .027, indice === 0 ? crema : negro);
        for (let cuerda = 0; cuerda < cuerdas; cuerda++) {
            caja((cuerda - (cuerdas - 1) / 2) * espacioCuerdas, y, .177, .01, .015, .009, metal);
        }
    }
    caja(0, -1.06, .163, .22, .10, .038, metal);
    const trastes = [];
    for (let traste = 0; traste < 19; traste++) {
        const y = 1.13 - 2.22 * (1 - 2 ** (-traste / 12));
        trastes.push(y);
        if (traste) caja(0, y, .155, .158 + (1.13 - y) * .037, .008, .009, metal);
        if ([3, 5, 7, 9, 12, 15, 17].includes(traste)) {
            const posicion = (y + trastes[traste - 1]) / 2;
            if (traste === 12) {
                disco(-.044, posicion, .011, .153, .155, crema);
                disco(.044, posicion, .011, .153, .155, crema);
            } else {
                disco(0, posicion, .013, .153, .155, crema);
            }
        }
    }
    for (let cuerda = 0; cuerda < cuerdas; cuerda++) {
        caja((cuerda - (cuerdas - 1) / 2) * espacioCuerdas, .04, .184,
            (bajo ? .006 : .003) + cuerda * .00055, 2.2, .006, metal);
        const lado = bajo || cuerda < 3 ? -1 : 1;
        const y = bajo ? 1.19 + cuerda * .117 : 1.22 + (cuerda % 3) * .118;
        caja(lado * .146, y, .024, .09, .045, .065, metal);
        disco(lado * .074, y, .022, .109, .141, metal);
    }
    for (const [x, y] of [[.30, -.94], [.32, -1.08], [.28, -1.21]]) {
        disco(x, y, .04, .134, .185, negro);
        disco(x, y, .027, .184, .19, metal);
    }
    if (bajo) {
        // Alarga el mástil con respecto al cuerpo y vuelve a normalizar las normales.
        for (let i = 0; i < vertices.length; i += 10) {
            vertices[i] *= .88;
            vertices[i + 1] = vertices[i + 1] * 1.12 + .13;
            if (vertices[i + 1] > -.35) vertices[i + 1] += (vertices[i + 1] + .35) * .12;
            const y = vertices[i + 4] / (vertices[i + 1] > -.35 ? 1.2544 : 1.12);
            const x = vertices[i + 3] / .88;
            const z = vertices[i + 5];
            const longitud = Math.hypot(x, y, z);
            vertices[i + 3] = x / longitud;
            vertices[i + 4] = y / longitud;
            vertices[i + 5] = z / longitud;
        }
    }
    return new Float32Array(vertices);
}
