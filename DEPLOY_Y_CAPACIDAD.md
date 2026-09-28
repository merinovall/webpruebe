> VERSIÓN 4: lee primero LEEME_PRIMERO.md. Este documento conserva información y pruebas de la versión 3; no certifica las nuevas integraciones.

# Web Astral · despliegue y capacidad

Esta es una aplicación web, accesible desde navegadores. El archivo .bat solo inicia un servidor local para probarla; no es una aplicación de escritorio ni publica por sí mismo la web.

## Dos modos incluidos

1. **Prueba local:** Python + Waitress + SQLite. INICIAR_WINDOWS.bat, como antes.
2. **Configuración para servidor:** Nginx sirve imágenes/CSS/JS y distribuye peticiones a Gunicorn (2 procesos × 4 hilos por defecto); PostgreSQL guarda los datos compartidos. Cada proceso usa un pool de hasta 8 conexiones. Se incluye Docker Compose para montar esta configuración.

No se ofrece capacidad infinita ni inmunidad a saturación. La capacidad depende de CPU, RAM, disco, red, base de datos y mezcla de solicitudes. Las operaciones de contraseña consumen más CPU y memoria que consultar habitaciones.

## Qué protege las reservas

- Transacciones de escritura en SQLite; bloqueo por tipo de habitación en PostgreSQL.
- Restricción de exclusión PostgreSQL para impedir estancias solapadas sobre la misma unidad física.
- Clave de solicitud única por usuario para que reintentar el envío del mismo formulario no cree otra reserva.
- Importes y disponibilidad calculados en servidor.
- Pool PostgreSQL limitado, espera de 3 segundos, timeout SQL de 5 segundos y bloqueo de 3 segundos.
- Respuesta 503 con Retry-After cuando se agota la espera; límites de frecuencia y respuesta 429 en el proxy.
- Los POST no se reenvían automáticamente desde Nginx a otra instancia.

## Preparar Docker Compose

Requiere Docker con Compose, disponible en el servidor elegido.

1. Copia `.env.example` como `.env`.
2. Genera dos secretos diferentes con `python -c "import secrets; print(secrets.token_hex(32))"`.
3. Completa POSTGRES_PASSWORD y SECRET_KEY con esos valores hexadecimales. No los publiques.
4. Ejecuta `docker compose up --build -d`.
5. Abre http://localhost:8080. La base se inicializa una sola vez mediante el servicio init antes de iniciar los procesos web.
6. Crea tu administrador: `docker compose exec web python app.py create-admin`.

El Compose está enlazado a 127.0.0.1 deliberadamente: este es el punto de partida local del despliegue. La base PostgreSQL no expone puertos públicos. El volumen pgdata conserva los datos.

## Publicar en Internet

Configura el dominio, certificados TLS y HTTPS en tu infraestructura. Para HTTPS terminado en Nginx, configura `listen 443 ssl`, certificados montados como solo lectura y puertos públicos. Activa HOTEL_HTTPS=1. No expongas directamente Gunicorn ni PostgreSQL. Si usas un balanceador/CDN delante de Nginx, configura únicamente sus rangos de IP como proxies de confianza y preserva el esquema HTTPS; de lo contrario se pierde la IP del cliente y los límites podrían aplicarse a todos los visitantes conjuntamente.

TRUST_PROXY=1 solo se debe usar con Gunicorn inaccesible directamente y detrás del proxy de confianza. La configuración incluida sobrescribe las cabeceras de cliente desde Nginx. No aceptes cabeceras arbitrarias enviadas directamente desde Internet.

Antes de producción: separa el rol de migraciones del rol limitado de la aplicación, configura respaldo de PostgreSQL y restauración probada, alertas, retención de datos y supervisión. El ejemplo Compose usa una sola cuenta de base de datos para facilitar la instalación inicial; no es una arquitectura de alta disponibilidad completa.

## Escalar de forma controlada

Puedes aumentar procesos o añadir instancias web detrás de un balanceador compatible, con el mismo DATABASE_URL, SECRET_KEY y hotel.json. Configura explícitamente todos los destinos del balanceador; cambiar el número de contenedores por sí solo no garantiza reparto adecuado. El PostgreSQL compartido y el control transaccional sustituyen al archivo SQLite por proceso.

Antes de aumentar réplicas calcula conexiones: réplicas × procesos × DB_POOL_SIZE, más migraciones, administración y monitoreo. El pool limita recursos; no crea capacidad extra en PostgreSQL. No uses SQLite compartido por NFS para este modo. Con tráfico elevado, usa almacenamiento/CDN de imágenes, PgBouncer cuando corresponda y PostgreSQL gestionado con respaldo y réplicas según el presupuesto. No hay autoscaling automático instalado.

## Pruebas realizadas y límites

`RESULTADO_CARGA.json` contiene una prueba HTTP local aislada: 20 solicitudes simultáneas para 2 unidades; 2 aceptadas y 18 rechazadas por falta de disponibilidad, sin sobreventas. Cinco reintentos del mismo formulario produjeron una sola reserva. Se ejecutaron 200 consultas de disponibilidad con concurrencia 20, todas correctas.

Este ensayo usa Waitress y SQLite en loopback; sus latencias no predicen el rendimiento en Internet ni el máximo de usuarios de un hosting. El conjunto Docker/Nginx/PostgreSQL fue preparado pero **no se pudo ejecutar ni medir en este entorno**, que no dispone de Docker/PostgreSQL operativo. Debe validarse en el servidor de destino antes de recibir reservas reales. No se afirma que el modo PostgreSQL haya superado una prueba de carga.

Puedes repetir la prueba local con `python test_concurrency.py`. Siempre crea una base temporal; no apunta a un hotel real. `python tests.py` comprueba el flujo funcional. Para producción realiza después una prueba escalonada sobre un entorno de ensayo propio, observa p95, errores, memoria, CPU, conexiones y bloqueos, y ajusta los límites con esas mediciones.

Programa limpieza periódica de contadores expirados de la tabla attempts y un plan de conservación de los registros personales. No elimines reservas activas para liberar espacio.

Referencias técnicas consultadas:
- https://www.psycopg.org/psycopg3/docs/advanced/pool.html
- https://www.postgresql.org/docs/current/rangetypes.html
- https://flask.palletsprojects.com/en/stable/deploying/gunicorn/
