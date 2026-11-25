# JORGE'S MUSIC HOME

Catálogo e inventario web de instrumentos musicales. El proyecto permite registrar, consultar, editar y eliminar instrumentos con una interfaz vintage. Se desarrolló para la Evaluación Sumativa N.º 2 de Programación Backend de INACAP.

## Requisitos

- Python 3.12 para Windows y PowerShell.
- XAMPP con MariaDB. El entorno de referencia usa MariaDB 10.11.
- Django 5.0.14 y mysqlclient 2.2.8. El archivo `requirements.txt` fija las versiones directas y transitivas.
- Node.js 20 o posterior para ejecutar las pruebas de JavaScript. El frontend usa HTML, CSS y JavaScript sin dependencias de Node.

## Instalación en Windows

Abre PowerShell en la carpeta que contiene `manage.py`. Instala Python 3.12 desde su distribuidor oficial y ejecuta:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Si PowerShell impide la activación, ejecuta los mismos comandos con `.\.venv\Scripts\python.exe` en lugar de `python`.

### MariaDB y variables de entorno

1. En el panel de XAMPP, inicia **MySQL**, que es el servicio MariaDB de esta instalación. Confirma el puerto local. Este ejemplo usa `3306`.
2. Con una cuenta autorizada para administrar la instancia, abre el cliente SQL de MariaDB. Si usas phpMyAdmin, inicia también Apache. Ejecuta esta instrucción para crear una base vacía de demostración:

   ```sql
   CREATE DATABASE jmhdemo CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
   ```

   La cuenta que usará Django debe tener acceso a `jmhdemo` y permisos para aplicar migraciones. Para `manage.py test`, debe poder crear y retirar un esquema independiente, `test_jmhdemo`, y aplicar sus migraciones. Configura esos permisos solo sobre los esquemas de trabajo y pruebas.
3. Copia la plantilla a la raíz del proyecto:

   ```powershell
   Copy-Item .env.example .env
   ```

4. Genera una clave exclusiva para tu instalación. Este comando reemplaza el marcador de la plantilla en `.env` sin mostrar la clave:

   ```powershell
   python -c "from pathlib import Path; from django.core.management.utils import get_random_secret_key; p = Path('.env'); p.write_text(p.read_text(encoding='utf-8-sig').replace('reemplaza-por-una-clave-local-generada', get_random_secret_key(), 1), encoding='utf-8')"
   ```

   Completa `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST` y `DB_PORT` con los datos de tu entorno. El archivo usa una asignación literal `NOMBRE=valor` por línea, sin comillas ni comentarios al final. Las líneas que empiezan con `#` son comentarios. Las variables del proceso tienen prioridad sobre el archivo. Mantén `.env` privado. Para la demostración en localhost, usa `DJANGO_DEBUG=1`.

### Migraciones y servidor

Con la base vacía configurada:

```powershell
python manage.py check
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

En una base vacía, `migrate` aplica `0005` y luego `0006`, que carga 16 instrumentos de ejemplo: cuatro guitarras, cuatro bajos, cuatro teclados y cuatro baterías. Los nombres indican el tipo de instrumento y las descripciones indican el modelo. El inventario queda disponible en `/instrumentos/`.

En una base existente se conservan los registros previos. La carga omite coincidencias por categoría, marca y modelo en la descripción. Si la descripción no identifica el modelo, la carga no puede reconocer esa coincidencia. Django registra `0006` como aplicada, por lo que volver a ejecutar `migrate` conserva los cambios y los borrados hechos desde el CRUD. La migración de datos es irreversible para proteger esos registros editables.

| Dirección local | Uso |
| --- | --- |
| `http://127.0.0.1:8000/` | Fachada interactiva. Las puertas abren la recepción. |
| `http://127.0.0.1:8000/recepcion/` | Recepción y menú principal |
| `http://127.0.0.1:8000/coleccion/` | Galería de cuatro categorías |
| `http://127.0.0.1:8000/coleccion/guitarras/` | Visor de guitarra y registros actuales |
| `http://127.0.0.1:8000/instrumentos/` | Catálogo y acceso a las acciones |
| `http://127.0.0.1:8000/instrumentos/nuevo/` | Formulario de alta |

En la fachada, entra por las puertas con clic, toque o **Tab + Enter**. Con movimiento reducido, el enlace abre la recepción directamente. Desde allí, **Inventario** abre el catálogo y **Agregar instrumento** lleva al formulario existente.

Desde cada tarjeta puedes abrir la ficha (**READ**), editar el registro precargado (**UPDATE**) o abrir la confirmación de borrado (**DELETE**). El formulario de alta realiza **CREATE**. El borrado se ejecuta al confirmar con un POST protegido por CSRF.

## Límites de los campos

| Campo | Regla |
| --- | --- |
| Nombre | De 2 a 20 caracteres. Letras, tildes, ñ, espacios internos y guiones. Se normalizan los espacios. |
| Marca | Fender, Gibson, Yamaha, Roland e Ibanez. |
| Categoría | Guitarras, Bajos, Teclados y Baterías. |
| Precio | Entero de $1 a $999.999 CLP, con hasta seis dígitos. `$100.000` se almacena como `100000`. |
| Stock | Entero de 0 a 999. |
| Descripción | Opcional, hasta 100 caracteres. |

## Pruebas

```powershell
python manage.py check
python manage.py test
node --preserve-symlinks --preserve-symlinks-main --test instrumentos/tests_js
```

Django crea y retira un esquema de pruebas separado. Las pruebas JavaScript usan eventos simulados y se complementan con la comprobación manual descrita en la [matriz de validaciones](docs/07_pruebas/matriz_validaciones.md). Consulta también las [reglas de campos](docs/06_validaciones/reglas_campos.md).

## Uso local y académico

La rama `feature/galeria-3d` parte del inventario vintage (`00440612826423e47646b62173e16d4b2e956c13`). Integra primero ese inventario al preparar la integración de la galería con `main`.

Desde **Instrumentos** en la recepción se accede a **Nuestra colección**. Las cuatro salas comparten un carrusel circular con registros actuales de MariaDB, giro independiente y diálogo de especificaciones. Cada categoría tiene una malla WebGL provisional y aplica el acabado de marca únicamente a las piezas pintadas. Los datos siguen disponibles si WebGL o JavaScript fallan. [Rutas, alcance de los modelos y revisión visual](docs/04_casos_de_uso/galeria.md)

Ejecuta la demostración en `127.0.0.1` y usa una base con datos de ejemplo. Esta versión no está preparada para despliegue público. El servidor de desarrollo, el modo de depuración y las acciones de inventario sin inicio de sesión están destinados a la demostración local.
