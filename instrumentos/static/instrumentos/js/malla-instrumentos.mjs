export function crearMalla() {
    const vertices = [];
    const unidad = (vector) => {
        const longitud = Math.hypot(...vector);
        return vector.map((valor) => valor / longitud);
    };
    const triangulo = (puntos, normales, color, acabado) => {
        for (const [indice, punto] of puntos.entries()) {
            vertices.push(...punto, ...normales[indice], ...color, Number(acabado));
        }
    };
    function caja([x, y, z], [ancho, alto, fondo], color, acabado = false) {
        const esquinas = Array.from({length: 8}, (_, i) => [
            x + (i & 1 ? .5 : -.5) * ancho,
            y + (i & 2 ? .5 : -.5) * alto,
            z + (i & 4 ? .5 : -.5) * fondo,
        ]);
        for (const [a, b, c, d, normal] of [
            [0, 2, 6, 4, [-1, 0, 0]], [1, 5, 7, 3, [1, 0, 0]],
            [0, 4, 5, 1, [0, -1, 0]], [2, 3, 7, 6, [0, 1, 0]],
            [0, 1, 3, 2, [0, 0, -1]], [4, 6, 7, 5, [0, 0, 1]],
        ]) {
            const normales = [normal, normal, normal];
            triangulo([esquinas[a], esquinas[b], esquinas[c]], normales, color, acabado);
            triangulo([esquinas[a], esquinas[c], esquinas[d]], normales, color, acabado);
        }
    }

    function cilindro(inicio, fin, radioInicio, radioFin, color, acabado = false) {
        const eje = unidad(fin.map((valor, i) => valor - inicio[i]));
        const invertido = eje.map((valor) => -valor);
        const u = unidad(Math.abs(eje[1]) > .9 ? [0, eje[2], -eje[1]] : [eje[2], 0, -eje[0]]);
        const v = [
            eje[1] * u[2] - eje[2] * u[1],
            eje[2] * u[0] - eje[0] * u[2],
            eje[0] * u[1] - eje[1] * u[0],
        ];
        const lado = (i) => u.map((valor, j) =>
            valor * Math.cos(i * Math.PI / 16) + v[j] * Math.sin(i * Math.PI / 16));
        const sumar = (centro, direccion, radio) => centro.map((valor, j) => valor + direccion[j] * radio);
        for (let i = 0; i < 32; i++) {
            const a = lado(i), b = lado(i + 1);
            const p = sumar(inicio, a, radioInicio), q = sumar(inicio, b, radioInicio);
            const r = sumar(fin, a, radioFin), s = sumar(fin, b, radioFin);
            triangulo([p, q, s], [a, b, b], color, acabado);
            triangulo([p, s, r], [a, b, a], color, acabado);
            triangulo([inicio, q, p], [invertido, invertido, invertido], color, acabado);
            triangulo([fin, r, s], [eje, eje, eje], color, acabado);
        }
    }
    return {caja, cilindro, vertices: () => new Float32Array(vertices)};
}
