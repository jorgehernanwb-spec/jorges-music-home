const vertice = `
    attribute vec3 posicion, normal, material;
    attribute float usaAcabado;
    uniform vec2 giro, escala;
    uniform vec3 acabado;
    uniform float altura;
    varying vec3 color, direccion, posicionEscena;
    varying float laca;

    vec3 orientar(vec3 v) {
        float sy = sin(giro.x), cy = cos(giro.x);
        float sx = sin(giro.y), cx = cos(giro.y);
        vec3 r = vec3(cy * v.x + sy * v.z, v.y, -sy * v.x + cy * v.z);
        return vec3(r.x, cx * r.y - sx * r.z, sx * r.y + cx * r.z);
    }

    void main() {
        vec3 punto = orientar(posicion - vec3(0.0, 0.03, 0.0));
        gl_Position = vec4(vec2(punto.x, punto.y + altura) * escala,
                           -punto.z * 0.25, 1.0 - punto.z * 0.17);
        direccion = orientar(normal);
        posicionEscena = punto;
        color = mix(material, acabado, usaAcabado);
        laca = usaAcabado;
    }
`;

const fragmento = `
    precision mediump float;
    varying vec3 color, direccion, posicionEscena;
    varying float laca;

    void main() {
        vec3 normal = normalize(direccion);
        vec3 luzPrincipal = normalize(vec3(-0.85, 1.9, 2.65) - posicionEscena);
        vec3 vista = normalize(vec3(0.0, 0.0, 5.88) - posicionEscena);
        vec3 media = normalize(luzPrincipal + vista);
        float luz = max(dot(normal, luzPrincipal), 0.0);
        float rebote = max(dot(normal, normalize(vec3(0.9, 0.2, -0.8))), 0.0);
        float reflejo = pow(max(dot(normal, media), 0.0), mix(16.0, 30.0, laca));
        float borde = pow(1.0 - max(dot(normal, vista), 0.0), 3.0);
        vec3 iluminacion = vec3(0.35, 0.33, 0.31)
                         + luz * vec3(0.84, 0.75, 0.63)
                         + rebote * vec3(0.54, 0.36, 0.20);
        vec3 brillo = (reflejo * mix(0.12, 0.31, laca) + borde * 0.09)
                    * vec3(1.0, 0.81, 0.59);
        gl_FragColor = vec4(color * iluminacion + brillo, 1.0);
    }
`;

function crearShader(gl, tipo, fuente) {
    const shader = gl.createShader(tipo);
    gl.shaderSource(shader, fuente);
    gl.compileShader(shader);
    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
        throw new Error(gl.getShaderInfoLog(shader));
    }
    return shader;
}

export function crearRenderizador(canvas, modelo) {
    const gl = canvas.getContext("webgl", {alpha: true, depth: true, antialias: true});
    if (!gl) throw new Error("WebGL no está disponible");

    const programa = gl.createProgram();
    const shaders = [
        crearShader(gl, gl.VERTEX_SHADER, vertice),
        crearShader(gl, gl.FRAGMENT_SHADER, fragmento),
    ];
    for (const shader of shaders) gl.attachShader(programa, shader);
    gl.linkProgram(programa);
    for (const shader of shaders) gl.deleteShader(shader);
    if (!gl.getProgramParameter(programa, gl.LINK_STATUS)) {
        throw new Error(gl.getProgramInfoLog(programa));
    }

    const malla = modelo.malla();
    if (!malla.length || malla.length % 30) throw new Error("Geometría inválida");
    const buffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
    gl.bufferData(gl.ARRAY_BUFFER, malla, gl.STATIC_DRAW);
    gl.useProgram(programa);
    for (const [nombre, tamaño, inicio] of [
        ["posicion", 3, 0], ["normal", 3, 3], ["material", 3, 6], ["usaAcabado", 1, 9],
    ]) {
        const ubicacion = gl.getAttribLocation(programa, nombre);
        gl.enableVertexAttribArray(ubicacion);
        gl.vertexAttribPointer(ubicacion, tamaño, gl.FLOAT, false, 40, inicio * 4);
    }

    const giro = gl.getUniformLocation(programa, "giro");
    const escala = gl.getUniformLocation(programa, "escala");
    const altura = gl.getUniformLocation(programa, "altura");
    const acabado = gl.getUniformLocation(programa, "acabado");
    gl.enable(gl.DEPTH_TEST);
    gl.clearColor(0, 0, 0, 0);
    return (horizontal, vertical, elevacion, color) => {
        const densidad = Math.min(globalThis.devicePixelRatio || 1, 2);
        const ancho = Math.max(1, Math.round(canvas.clientWidth * densidad));
        const alto = Math.max(1, Math.round(canvas.clientHeight * densidad));
        if (canvas.width !== ancho || canvas.height !== alto) {
            canvas.width = ancho;
            canvas.height = alto;
        }

        gl.viewport(0, 0, gl.drawingBufferWidth, gl.drawingBufferHeight);
        gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
        const proporcion = gl.drawingBufferWidth / gl.drawingBufferHeight;
        const ajuste = modelo.escala * Math.min(1, proporcion / modelo.anchoMinimo);
        gl.uniform2f(escala, ajuste / proporcion, ajuste);
        gl.uniform2f(giro, horizontal, vertical);
        gl.uniform1f(altura, elevacion);
        gl.uniform3fv(acabado, color);
        gl.drawArrays(gl.TRIANGLES, 0, malla.length / 10);
    };
}
