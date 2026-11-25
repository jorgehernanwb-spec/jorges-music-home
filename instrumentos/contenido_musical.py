"""Artículos editoriales versionados, en el orden de la portada."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Articulo:
    slug: str
    tema: str
    titulo: str
    imagen: str
    entrada: str
    secciones: tuple[tuple[str, tuple[str, ...]], ...]
    cierre: str
    fuentes: tuple[tuple[str, str], ...]


INSTRUMENTOS = "Instrumentos"
HISTORIA = "Historia y acontecimientos"
TECNOLOGIA = "Tecnología y curiosidades"

ARTICULOS = {articulo.slug: articulo for articulo in (
    Articulo(
        "guitarra", INSTRUMENTOS, "Guitarra — Mucho más que seis cuerdas",
        "Guitarra acústica de madera bajo luz cálida",
        "La guitarra puede acompañar una voz, llevar la melodía o sostener por sí sola una pieza. Su sonido nace de una cuerda que vibra y cambia según cómo se pulse y cómo el instrumento amplifique esa vibración.",
        (
            ("Una forma que fue evolucionando", (
                "La guitarra moderna fue tomando forma a partir de instrumentos de cuerda anteriores. En la España del siglo XIX, constructores como Antonio de Torres ayudaron a establecer las proporciones y soluciones de construcción asociadas hoy con la guitarra clásica. Con el tiempo se consolidaron también modelos acústicos de cuerdas de acero y guitarras eléctricas.",
            )),
            ("Del clavijero a la caja", (
                "Las clavijas ajustan la tensión. Los trastes dividen el diapasón y, al presionar una cuerda, determinan qué tramo queda libre para vibrar. En una acústica, el puente transmite la vibración a la tapa y la caja contribuye a proyectar el sonido. En una eléctrica de pastillas magnéticas, la vibración de la cuerda metálica se convierte en señal que puede amplificarse.",
            )),
            ("Afinar y tocar el primer acorde", (
                "La afinación estándar, de grave a aguda, es Mi, La, Re, Sol, Si y Mi. Afina una cuerda por vez. Luego prueba Mi menor: presiona el segundo traste de las cuerdas La y Re y deja sonar las demás al aire. Toca cada cuerda por separado para descubrir si alguna queda apagada.",
            )),
        ),
        "Antes de aumentar la velocidad, busca un sonido limpio y un pulso que puedas mantener.",
        (("The Met · La guitarra española", "https://www.metmuseum.org/es/essays/the-spanish-guitar"),
         ("Yamaha · Cómo produce sonido la guitarra acústica", "https://www.yamaha.com/en/musical_instrument_guide/acoustic_guitar/mechanism/")),
    ),
    Articulo(
        "bajo", INSTRUMENTOS, "Bajo — El corazón de las frecuencias graves",
        "Bajo eléctrico apoyado en una superficie de madera",
        "El bajo enlaza lo que hacen la batería y los instrumentos armónicos. Una sola nota bien colocada puede aclarar el acorde y darle dirección a todo un compás.",
        (
            ("Cuatro cuerdas y un registro diferente", (
                "El bajo eléctrico habitual de cuatro cuerdas se afina Mi, La, Re y Sol, una octava por debajo de las cuatro cuerdas graves de una guitarra estándar. Usa cuerdas más gruesas y suele tener mayor longitud de escala, es decir, más distancia de cuerda vibrante entre la cejuela y el puente.",
                "En un bajo eléctrico de pastillas magnéticas, la cuerda metálica vibrante altera el campo magnético y produce una señal que un amplificador convierte en sonido audible. El Precision Bass presentado por Fender en 1951 fue un modelo influyente para la difusión del bajo eléctrico con trastes.",
            )),
            ("Escuchar antes de llenar el compás", (
                "Un bajista puede tocar la nota fundamental de un acorde para establecer el centro armónico o elegir otra nota para cambiar la sensación de la progresión. También controla cuándo termina cada sonido. Alternar notas cortas y largas altera el ritmo aunque se mantengan las mismas alturas.",
            )),
            ("Ejercicio de pulso", (
                "Cuenta cuatro pulsos por compás. Toca La en el primero y en el tercero. Luego cambia a Re y repite. Cuando el pulso sea estable, intenta coincidir con el bombo de una grabación sencilla y deja silencio en los otros pulsos.",
            )),
        ),
        "Escucha qué cambia en el conjunto al variar la duración de una nota, incluso si su altura sigue siendo la misma.",
        (("Fender · Historia del Precision Bass", "https://www.fender.com/articles/behind-the-scenes/legendary-lows-the-precision-bass-story"),),
    ),
    Articulo(
        "teclado", INSTRUMENTOS, "Teclado — De las teclas al sonido digital",
        "Teclado digital con teclas blancas y negras",
        "Un teclado organiza las notas para que podamos ver sus relaciones. La misma disposición permite accionar un piano acústico, controlar un sintetizador o ejecutar sonidos en una computadora.",
        (
            ("Encontrar una octava", (
                "Las teclas negras se repiten en grupos de dos y tres. La tecla blanca inmediatamente a la izquierda de cada grupo de dos es Do. Desde ese Do hasta el siguiente hay una octava, con doce semitonos en el sistema habitual de teclas blancas y negras.",
                "Las notas separadas por una octava comparten nombre, pero la más aguda tiene el doble de frecuencia. Un teclado puede tener menos teclas que un piano de 88 y conservar este mismo patrón.",
            )),
            ("De la acción mecánica a los sensores", (
                "En un piano acústico, la tecla acciona un mecanismo que impulsa un martillo contra cuerdas. Un instrumento digital usa sensores para detectar la pulsación. Según el equipo, reproduce muestras grabadas o genera sonido por síntesis, y puede cambiar su respuesta según la velocidad de la pulsación.",
            )),
            ("Una mano, tres funciones", (
                "Toca Do, Mi y Sol juntos. Repite el acorde con un sonido de piano y después con uno de órgano o cuerdas. Las notas son las mismas, pero cambian el inicio del sonido, su duración y su color. Si conectas el teclado como controlador MIDI, esas pulsaciones también pueden dirigir un instrumento virtual.",
            )),
        ),
        "La distribución de notas se conserva aunque cambie la tecnología que produce el sonido.",
        (("Yamaha · Piano acústico o digital", "https://www.yamaha.com/en/musical_instrument_guide/piano/selection/selection002.html"),
         ("The MIDI Association · Historia de MIDI", "https://midi.org/midi-history-chapter-6-midi-begins-1981-1983")),
    ),
    Articulo(
        "bateria", INSTRUMENTOS, "Batería — El motor del ritmo",
        "Batería acústica con tambores, platillos y soportes",
        "La batería reúne elementos que una persona toca con las manos y los pies. Cada pieza aporta un ataque y una duración diferentes, lo que permite construir patrones con varias capas.",
        (
            ("Un conjunto para un solo intérprete", (
                "A fines del siglo XIX comenzaron a reunirse instrumentos de percusión en conjuntos que podía tocar una sola persona. El pedal del bombo permitió usar el pie para los graves y liberar las manos para otros golpes. La configuración evolucionó con la música y admite numerosas variantes.",
            )),
            ("Parches, metal y sensores", (
                "El bombo produce un golpe grave. La caja tiene bordones que vibran contra un parche y explican su sonido característico. Los toms ofrecen acentos de distintas alturas y los platillos marcan pulsos o transiciones. El charles combina dos platillos que se abren y cierran con un pedal.",
                "En una batería acústica vibran los parches, los cascos y los platillos. En una electrónica, los pads detectan los golpes y un módulo reproduce o genera los sonidos. Con auriculares se puede reducir el sonido amplificado, aunque los golpes físicos en los pads siguen siendo audibles.",
            )),
            ("Un compás de cuatro pulsos", (
                "Cuenta uno, dos, tres, cuatro a velocidad constante. Marca todos los pulsos con el charles, el uno y el tres con el bombo y el dos y el cuatro con la caja. Aprende cada parte por separado y agrega la siguiente cuando puedas repetir el patrón sin acelerar.",
            )),
        ),
        "Un ritmo sencillo y estable permite experimentar después con desplazamientos, silencios y variaciones de intensidad.",
        (("Yamaha · Origen, componentes y técnica de la batería", "https://www.yamaha.com/en/musical_instrument_guide/drums/"),),
    ),
    Articulo(
        "fonografo", HISTORIA, "El invento que permitió reproducir el sonido — 1877",
        "Ilustración conceptual de un fonógrafo de cilindro",
        "Hasta la segunda mitad del siglo XIX, escuchar una interpretación requería estar presente cuando ocurría. El fonógrafo demostró que una vibración podía quedar inscrita en un soporte y reproducirse después.",
        (
            ("De la voz a una huella física", (
                "En 1877 Thomas Edison investigaba cómo registrar señales. Para su fonógrafo, el mecánico John Kruesi construyó un dispositivo con un cilindro recubierto de papel de estaño. Al hablar frente a una membrana, la vibración movía una punta que marcaba el recubrimiento mientras el cilindro giraba.",
                "Al reproducirlo, otra punta seguía esa huella y hacía vibrar nuevamente una membrana. No se necesitaba convertir el sonido en números: el relieve mecánico guardaba el patrón de la vibración.",
            )),
            ("Demostración y patente", (
                "La fecha exacta de la primera prueba es discutida, pero la demostración pública de la tecnología se sitúa a fines de 1877. La patente estadounidense se concedió en febrero de 1878. El dispositivo llamó la atención pese a sus dificultades de uso y a la fragilidad del soporte de estaño.",
            )),
            ("De una prueba a un medio musical", (
                "Los cilindros posteriores de cera y otros formatos facilitaron el uso de grabaciones. La innovación decisiva fue separar la escucha del momento de la interpretación. A partir de ahí fue posible conservar voces, distribuir música y volver a oír un mismo pasaje.",
            )),
        ),
        "El problema que resolvió Edison sigue siendo reconocible: guardar una señal y reconstruirla de forma que podamos oírla.",
        (("Biblioteca del Congreso de EE. UU. · Historia del fonógrafo de cilindro", "https://www.loc.gov/collections/edison-company-motion-pictures-and-sound-recordings/articles-and-essays/history-of-edison-sound-recordings/history-of-the-cylinder-phonograph/"),),
    ),
    Articulo(
        "vinilo", HISTORIA, "La revolución del disco de vinilo — 1948",
        "Disco de vinilo negro sobre un tocadiscos",
        "Cuando un disco puede guardar varios temas por lado, cambia tanto la tecnología como la forma de organizar una escucha. El LP hizo más práctico dedicar un lado entero a una obra o secuencia musical.",
        (
            ("Surco fino, más tiempo", (
                "En junio de 1948, Columbia Records presentó su disco de larga duración de microsurco a 33⅓ revoluciones por minuto. Un LP de 12 pulgadas podía alojar alrededor de 23 minutos por cara. Una rotación más lenta y los surcos más próximos permitían más tiempo que los discos convencionales de goma laca a 78 rpm.",
            )),
            ("De la aguja al parlante", (
                "El surco contiene variaciones físicas que la aguja sigue mientras gira el disco. La cápsula convierte el movimiento en una señal eléctrica. En una configuración habitual, un previo de fono adapta esa señal y el equipo de audio la amplifica para escucharla.",
            )),
            ("El álbum y los formatos posteriores", (
                "El LP convivió con formatos de menor duración como el sencillo de 45 rpm. El casete facilitó grabar y transportar música; el CD ofreció audio digital en un disco óptico. Con archivos y servicios en línea, la canción pudo distribuirse independientemente de un soporte físico. El LP, en cambio, conserva una división audible entre sus caras.",
            )),
        ),
        "Al escuchar un LP completo, observa qué función cumple el orden de las pistas y dónde se decidió hacer la pausa.",
        (("Biblioteca del Congreso de EE. UU. · El primer disco de larga duración", "https://blogs.loc.gov/now-see-hear/2019/04/inside-the-archival-box-the-first-long-playing-disc/"),),
    ),
    Articulo(
        "woodstock", HISTORIA, "Woodstock — El festival que marcó una generación",
        "Ilustración de una multitud frente a un escenario al aire libre",
        "Entre el 15 y el 18 de agosto de 1969, Woodstock reunió actuaciones de rock, folk y otros estilos en una granja del estado de Nueva York, en un momento de intensos cambios culturales.",
        (
            ("El festival se llamó Woodstock y ocurrió en Bethel", (
                "El nombre se mantuvo aunque el lugar definitivo fue Bethel. El programa se planeó para tres días, pero el mal tiempo, el tráfico y los retrasos extendieron las actuaciones hasta la mañana del lunes 18. La diferencia entre el programa previsto y lo vivido forma parte de la historia del festival.",
            )),
            ("Música y contexto", (
                "La oposición a la guerra de Vietnam, las luchas por derechos civiles y la experimentación artística marcaron el contexto estadounidense de la época. En el escenario convivieron artistas con lenguajes distintos, entre ellos Richie Havens, Santana y Jimi Hendrix. Esa variedad ayuda a explicar por qué el festival se recuerda como un acontecimiento cultural además de musical.",
            )),
            ("Cómo leer el acontecimiento", (
                "La memoria pública suele concentrarse en imágenes de público, lluvia y actuaciones memorables. Los programas, las fotografías y los testimonios permiten contrastar esa imagen con detalles concretos: el lugar, las jornadas y los cambios de horario. Examinar ambos planos evita confundir el símbolo con una descripción completa de lo que ocurrió.",
            )),
        ),
        "Woodstock es un buen punto de partida para estudiar cómo un concierto se convierte en memoria colectiva.",
        (("Bethel Woods Center for the Arts · Historia de Woodstock", "https://www.bethelwoodscenter.org/museum/woodstock-history"),),
    ),
    Articulo(
        "hip-hop", HISTORIA, "El nacimiento del hip-hop",
        "Tocadiscos y cajas de discos en una escena inspirada en el Bronx",
        "El hip-hop tomó forma en el Bronx de Nueva York durante los años setenta. Las fiestas comunitarias ofrecían espacio para que DJ, MC y bailarines transformaran discos y ritmos conocidos en actuaciones nuevas.",
        (
            ("El break como material de trabajo", (
                "Un break es un pasaje donde se destaca el ritmo. Con dos copias de un disco y dos tocadiscos, un DJ puede volver al inicio del fragmento en uno mientras el otro lo reproduce. Esa alternancia extiende la sección instrumental y da más tiempo a quienes bailan o improvisan sobre ella.",
            )),
            ("Un hito y una cultura comunitaria", (
                "La fiesta organizada por Cindy Campbell y musicalizada por DJ Kool Herc el 11 de agosto de 1973 se recuerda como un hito. Ese encuentro ayuda a situar el origen del hip-hop, que surgió de la actividad de muchas personas y comunidades. El trabajo de DJ, las rimas del MC, el breaking y el arte del grafiti suelen mencionarse como expresiones centrales de esa cultura.",
            )),
            ("Del encuentro local a la grabación", (
                "Con la grabación comercial, la producción de estudio y la circulación internacional, las técnicas y estilos se multiplicaron. Para escuchar una canción con atención, separa sus capas: identifica el pulso, la repetición instrumental y cómo el fraseo de la voz se apoya en el ritmo o se aparta de él.",
            )),
        ),
        "Su historia muestra cómo una comunidad puede transformar herramientas de reproducción en herramientas de creación.",
        (("Museo Nacional de Historia Estadounidense · El hip-hop en el Smithsonian", "https://americanhistory.si.edu/press/releases/hip-hop-comes-smithsonian"),),
    ),
    Articulo(
        "walkman", TECNOLOGIA, "Cuando la música se volvió portátil — 1979",
        "Reproductor portátil de casetes con auriculares",
        "El Walkman de Sony reunió un reproductor estéreo de casetes y auriculares ligeros. La música grabada pudo acompañar un trayecto cotidiano sin depender de un equipo instalado en una habitación.",
        (
            ("El TPS-L2 y la escucha personal", (
                "Sony lanzó el TPS-L2 en Japón en 1979. El diseño se orientó a la reproducción portátil. El uso de baterías y auriculares permitió moverse mientras se escuchaba, y convirtió la elección musical en una experiencia más individual en espacios compartidos.",
            )),
            ("La cinta y su recorrido", (
                "El casete almacena una señal en cinta magnética. Un cabezal lee los cambios magnéticos mientras la cinta avanza, y el circuito del equipo amplifica la señal para los auriculares. Cambiar de canción suele implicar avanzar o rebobinar. Esa limitación da más importancia al orden de una recopilación.",
            )),
            ("De un casete a una biblioteca", (
                "Los reproductores portátiles de discos y, después, los de archivos digitales y los teléfonos ampliaron la cantidad de música transportable y facilitaron pasar de una pista a otra. El cambio cultural iniciado por la escucha portátil se mantiene: puedes escoger una banda sonora distinta para cada trayecto.",
            )),
        ),
        "Compara una lista pensada para un casete con una lista que puede reproducirse en orden aleatorio. La tecnología cambia las decisiones de quien la prepara.",
        (("Sony · Historia del Walkman", "https://www.sony.com/en/SonyInfo/CorporateInfo/History/SonyHistory/2-03.html"),),
    ),
    Articulo(
        "midi", TECNOLOGIA, "MIDI — El lenguaje de los instrumentos electrónicos",
        "Cable MIDI de cinco pines junto a un sintetizador",
        "MIDI permite que equipos diferentes compartan instrucciones de interpretación. Un teclado puede enviar qué nota se tocó y con qué intensidad; el dispositivo receptor decide cómo convertir esa instrucción en sonido.",
        (
            ("Eventos de interpretación", (
                "Una nota suele empezar con un mensaje Note On y terminar con Note Off. Otros mensajes permiten mover controles, cambiar sonidos o transmitir el pulso entre equipos. El mensaje MIDI describe una acción. El timbre sale del sintetizador o instrumento virtual que recibe esa acción.",
            )),
            ("Un acuerdo entre fabricantes", (
                "La cooperación de fabricantes a comienzos de los años ochenta permitió conectar equipos de marcas diferentes. En 1983 se demostró públicamente la comunicación entre sintetizadores de Sequential Circuits y Roland. Las conexiones originales de cinco pines siguen en uso y conviven con el transporte de mensajes por USB y otras conexiones.",
            )),
            ("Un ejemplo en el estudio", (
                "Graba un acorde desde un teclado hacia una estación de audio digital como eventos MIDI. Puedes subir una nota, cambiar su duración o sustituir el piano virtual por un sintetizador y conservar la misma interpretación. Si exportas el resultado como audio, ese archivo contiene el sonido ya renderizado.",
            )),
        ),
        "Al resolver un problema de conexión, identifica primero si quieres transferir instrucciones MIDI, audio o ambos.",
        (("The MIDI Association · Orígenes de MIDI, 1981–1983", "https://midi.org/midi-history-chapter-6-midi-begins-1981-1983"),),
    ),
    Articulo(
        "gusanos-musicales", TECNOLOGIA, "¿Por qué se nos queda pegada una canción?",
        "Auriculares sobre un motivo musical escrito",
        "A veces un fragmento musical reaparece en la mente sin que decidamos recordarlo. En investigación se llama imaginación musical involuntaria. En la vida cotidiana suele hablarse de un gusano musical.",
        (
            ("Qué vuelve a la memoria", (
                "Por lo general se repite un pasaje breve. Haber oído una canción recientemente, encontrar una palabra asociada o estar en un contexto familiar puede propiciar que ese recuerdo aparezca. La repetición favorece la familiaridad y la familiaridad facilita reconocer y anticipar lo que sigue.",
            )),
            ("Qué examinó un estudio", (
                "Kelly Jakubowski y sus colaboradores compararon melodías reportadas como pegadizas con otras canciones. Encontraron asociaciones con la popularidad, ciertos patrones en el contorno melódico y un tempo relativamente rápido dentro de su muestra. Son asociaciones estadísticas: el estudio no permite predecir qué canción recordará cada persona.",
            )),
            ("Una observación para hacer en casa", (
                "Anota cuándo aparece un fragmento, qué escuchaste antes y qué parte vuelve. Distingue una melodía completa de dos o tres versos repetidos. Al comparar varios días podrás reconocer pistas personales, aunque un registro individual no sustituye un estudio controlado.",
            )),
        ),
        "Un fragmento que vuelve solo muestra cómo la memoria musical puede activarse por asociación sin una búsqueda deliberada.",
        (("Jakubowski y colaboradores · Dissecting an Earworm", "https://www.apa.org/pubs/journals/releases/aca-aca0000090.pdf"),),
    ),
    Articulo(
        "la-440", TECNOLOGIA, "¿Por qué los músicos afinan con 440 Hz?",
        "Diapasón metálico sobre madera oscura",
        "El La situado por encima del Do central, llamado La4 en notación científica, suele fijarse en 440 Hz. Un hercio equivale a un ciclo por segundo, así que esa referencia corresponde a 440 ciclos en un segundo.",
        (
            ("Acordar un punto de partida", (
                "Si varios instrumentos deben tocar juntos, necesitan una referencia común. El La 440 ofrece un punto que pueden reproducir un diapasón, un afinador electrónico o un instrumento ya afinado. El NIST documenta su uso como referencia internacional y la emisión de la señal A440 por su estación WWV desde 1936.",
                "Algunos conjuntos adoptan otra referencia para ajustarse a su práctica o repertorio. Antes de una sesión compartida conviene comprobar qué frecuencia acordó el grupo.",
            )),
            ("Octavas y semitonos", (
                "La3 y La5 se obtienen al dividir o multiplicar por dos los 440 Hz: 220 y 880 Hz, respectivamente. En el temperamento igual de doce divisiones, cada semitono multiplica la frecuencia por la raíz duodécima de dos. Así se calculan las otras notas a partir de la referencia.",
            )),
            ("Probarlo con un afinador", (
                "Configura 440 Hz como referencia y toca un La. Observa si el indicador lo sitúa grave o agudo y ajusta en pasos pequeños. Si comparas un instrumento con otro que usa una referencia diferente, pueden discrepar aunque ambos indiquen la nota La.",
            )),
        ),
        "El valor de referencia permite que distintas personas afinen por separado y luego puedan tocar juntas.",
        (("NIST · Glosario de tiempo y frecuencia, A440", "https://tf.nist.gov/general/pdf/1548.pdf"),),
    ),
)}
