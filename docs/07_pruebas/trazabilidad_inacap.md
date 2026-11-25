# Trazabilidad de la evaluación INACAP

La pauta «Evaluación Sumativa · Aplicación Django + MySQL» de Programación Backend, Unidad 2, asigna 60 puntos al proyecto y 40 a la defensa individual. Esta matriz relaciona cada criterio con evidencia del repositorio. La calificación y la comprobación de los aportes corresponden al docente.

| Criterio oficial | Puntos | Evidencia y verificación |
| --- | ---: | --- |
| Configuración y funcionamiento de Django | 7 | `manage.py check`, configuración, URLs y plantillas. [Arquitectura](../02_arquitectura/mvt.md) |
| Conexión Django a MySQL/MariaDB | 10 | Backend MySQL de Django y pruebas de persistencia con MariaDB aislada. [Instalación](../../README.md#instalación-en-windows) |
| Modelo y estructura de base de datos | 8 | `Instrumento`, migraciones 0001–0006 y pruebas de carga inicial y restricciones SQL. [Reglas](../06_validaciones/reglas_campos.md) |
| Cumplimiento de la temática asignada | 8 | Tienda de música con entidad Instrumento, catálogo de ejemplo, inventario y colección. [Galería](../04_casos_de_uso/galeria.md) |
| CRUD a nivel BD y web | 12 | `InstrumentoCRUDTests` comprueba alta, detalle, cambios persistidos y baja con POST y CSRF. [Casos CRUD](../04_casos_de_uso/crud.md) |
| Formularios y validaciones | 5 | `crear.html` y `editar.html` son pantallas distintas que reutilizan `InstrumentoForm`. Pruebas Django y JavaScript cubren entradas válidas e inválidas. [Matriz](matriz_validaciones.md) |
| Interfaz y usabilidad | 5 | Navegación por fachada y Recepción, inventario con filtros, formularios separados y confirmación de borrado. [Navegación](../03_diagramas/navegacion.md) |
| Git/GitHub y uso de branches | 5 | Historial, ramas y commits disponibles mediante `git branch -vv`, `git log --oneline --graph --all` y `git show --stat <sha>`. Cada integrante debe identificar y demostrar su aporte. |
