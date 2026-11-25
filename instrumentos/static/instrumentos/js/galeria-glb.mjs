import {
    ACESFilmicToneMapping, Box3, DirectionalLight, Group, HemisphereLight,
    OrthographicCamera, PMREMGenerator, Scene, Sphere, WebGLRenderer,
} from "../vendor/three-0.180.0/three.module.min.mjs";
import {GLTFLoader} from "../vendor/three-0.180.0/GLTFLoader.mjs";
import {RoomEnvironment} from "../vendor/three-0.180.0/RoomEnvironment.mjs";
import {esPiezaPintable, urlModelo} from "./modelos-glb.mjs";

export function encuadrar(escena) {
    const esfera = new Box3().setFromObject(escena, true).getBoundingSphere(new Sphere());
    if (!(esfera.radius > 0 && Number.isFinite(esfera.radius))) throw new Error("Modelo sin volumen");
    const centro = new Group();
    centro.position.copy(esfera.center).negate();
    centro.add(escena);
    const instrumento = new Group();
    instrumento.scale.setScalar(1 / esfera.radius);
    instrumento.add(centro);
    return instrumento;
}

export function prepararAcabado(escena, modelo) {
    const clones = new Map();
    escena.traverse((objeto) => {
        if (!esPiezaPintable(objeto, modelo)) return;
        const original = objeto.material;
        if (!clones.has(original)) {
            const material = original.clone();
            const activo = {value: false};
            // El acabado sustituye el tinte de la textura, preservando su detalle tonal y sus canales PBR.
            material.onBeforeCompile = (shader) => {
                shader.uniforms.acabadoJmh = activo;
                shader.fragmentShader = `uniform bool acabadoJmh;\n${shader.fragmentShader}`.replace(
                    "#include <map_fragment>",
                    `
                    #ifdef USE_MAP
                        if (acabadoJmh) {
                            vec4 detalle = texture2D(map, vMapUv);
                            float luz = dot(detalle.rgb, vec3(0.2126, 0.7152, 0.0722));
                            diffuseColor *= vec4(vec3(mix(0.78, 1.20, luz)), detalle.a);
                        } else {
                            #include <map_fragment>
                        }
                    #endif
                    `,
                );
            };
            clones.set(original, {material, activo});
        }
        objeto.material = clones.get(original).material;
    });
    let actual;
    return {
        originales: [...clones.keys()],
        aplicar(hex) {
            if (hex === actual) return;
            actual = hex;
            const valido = /^#[\da-f]{6}$/i.test(hex);
            for (const [original, {material, activo}] of clones) {
                activo.value = valido;
                if (valido) material.color.set(hex);
                else material.color.copy(original.color);
            }
        },
    };
}

function liberarModelo(escena, originales) {
    const geometrias = new Set(), materiales = new Set(originales), texturas = new Set(), imagenes = new Set();
    escena.traverse((objeto) => {
        if (!objeto.isMesh) return;
        geometrias.add(objeto.geometry);
        for (const material of [].concat(objeto.material)) materiales.add(material);
    });
    for (const material of materiales) {
        for (const valor of Object.values(material)) if (valor?.isTexture) texturas.add(valor);
        material.dispose();
    }
    for (const textura of texturas) {
        imagenes.add(textura.image);
        textura.dispose();
    }
    for (const imagen of imagenes) imagen?.close?.();
    for (const geometria of geometrias) geometria.dispose();
}

export function crearRenderizador(canvas, modelo) {
    const opciones = {alpha: true, antialias: true};
    const contexto = canvas.getContext("webgl2", opciones);
    if (!contexto) throw new Error("WebGL 2 no está disponible");
    const renderer = new WebGLRenderer({canvas, context: contexto, ...opciones});
    renderer.toneMapping = ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.15;
    const escena = new Scene();
    const camara = new OrthographicCamera(-1, 1, 1, -1, .1, 15);
    camara.position.z = 4;
    const luz = new DirectionalLight(0xffe1b8, 2.1);
    luz.position.set(-2, 4, 5);
    const relleno = new DirectionalLight(0xffbb78, 1.1);
    relleno.position.set(3, 2, -4);
    escena.add(luz, relleno, new HemisphereLight(0xffecd8, 0x776052, 1.25));

    const abortar = new AbortController();
    let entorno, instrumento, fuente, acabado;
    let cerrado = false;
    let ancho = 0, alto = 0, densidad = 0;
    const listo = (async () => {
        const respuesta = await fetch(urlModelo(modelo), {signal: abortar.signal});
        if (!respuesta.ok) throw new Error(`GLB no disponible (${respuesta.status})`);
        const datos = await respuesta.arrayBuffer();
        if (cerrado) return false;
        const {scene} = await new GLTFLoader().parseAsync(datos, "");
        if (cerrado) {
            liberarModelo(scene, []);
            return false;
        }
        fuente = scene;
        instrumento = encuadrar(scene);
        acabado = prepararAcabado(scene, modelo);
        escena.add(instrumento);
        const generador = new PMREMGenerator(renderer);
        const sala = new RoomEnvironment();
        try {
            entorno = generador.fromScene(sala, .04);
            escena.environment = entorno.texture;
            escena.environmentIntensity = .8;
        } finally {
            sala.dispose();
            generador.dispose();
        }
        return true;
    })();

    return {
        listo,
        render(horizontal, vertical, elevacion, color) {
            if (cerrado || !instrumento) return;
            const nuevoAncho = Math.max(1, canvas.clientWidth);
            const nuevoAlto = Math.max(1, canvas.clientHeight);
            const nuevaDensidad = Math.min(globalThis.devicePixelRatio || 1, 2);
            if (ancho !== nuevoAncho || alto !== nuevoAlto || densidad !== nuevaDensidad) {
                [ancho, alto, densidad] = [nuevoAncho, nuevoAlto, nuevaDensidad];
                renderer.setPixelRatio(densidad);
                renderer.setSize(ancho, alto, false);
                const aspecto = ancho / alto;
                camara.top = modelo.margen / Math.min(aspecto, 1);
                camara.bottom = -camara.top;
                camara.right = camara.top * aspecto;
                camara.left = -camara.right;
                camara.updateProjectionMatrix();
            }
            instrumento.rotation.set(vertical, horizontal, 0, "XYZ");
            instrumento.position.y = elevacion;
            acabado.aplicar(color);
            renderer.render(escena, camara);
        },
        cerrar() {
            if (cerrado) return;
            cerrado = true;
            abortar.abort();
            if (fuente) liberarModelo(fuente, acabado?.originales ?? []);
            entorno?.dispose();
            renderer.dispose();
        },
    };
}
