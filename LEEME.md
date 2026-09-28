> VERSIÓN 4: lee primero LEEME_PRIMERO.md. Este documento conserva información y pruebas de la versión 3; no certifica las nuevas integraciones.

# Edición Astral — v3

Diseño oscuro en verde mineral y menta, tipografía Arial, movimiento suave e imagen nocturna generada. Las fotografías de interiores, tarifas e inventario siguen siendo ejemplos. El mapa y la fachada conservan la referencia de Río Negro.

**Es una web.** El iniciador Windows permite verla localmente; para recibir visitantes por Internet debes desplegar el servidor. Lee **DEPLOY_Y_CAPACIDAD.md** para el modo PostgreSQL/Gunicorn/Nginx, sus límites y pruebas pendientes.

Los apartados SQLite de esta guía se refieren al modo local. La configuración de producción y sus instrucciones actualizadas están en DEPLOY_Y_CAPACIDAD.md.

# Hospedaje Río Negro · EMB MERVAL

Proyecto web completo en español, con Arial, HTML/CSS/JavaScript y servidor Python/Flask + SQLite. Diseño propio inspirado en la distribución de la imagen entregada y en las secciones de https://hotelmayros.com/. No es una copia de su marca, textos ni fotografías.

## Abrir en Windows

1. Extrae TODO el ZIP en una carpeta, por ejemplo Documentos/HospedajeRioNegro.
2. Instala Python 3.12 o superior si aún no lo tienes (marca «Add Python to PATH»).
3. Haz doble clic en **INICIAR_WINDOWS.bat**. La primera vez se necesita Internet para instalar las dependencias.
4. Se abrirá http://127.0.0.1:5000. Mantén la consola abierta mientras uses la página.
5. Crea tu cuenta desde la ventana de bienvenida o pulsa «Continuar como visitante».

No se abre haciendo doble clic en el HTML ni con Live Server: el registro y las reservas necesitan el servidor Python. Si el puerto 5000 está ocupado, cierra la otra aplicación o define PORT con otro valor.

## Abrir en VS Code / terminal

Abre la carpeta del proyecto y ejecuta:

```powershell
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe iniciar.py
```

Linux/macOS:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python app.py
```

## Panel de recepción

Ejecuta **CREAR_ADMIN_WINDOWS.bat**. Elige un correo nuevo y una contraseña propia de al menos 10 caracteres; no se incluye ninguna cuenta predeterminada. Después inicia sesión en la web, entra en **Mi estancia → Panel de recepción**.

El panel muestra solicitudes, permite confirmar/cancelar reservas, completar estancias después de su fecha de salida, revisar/publicar/ocultar reseñas y leer consultas. Para responder consultas usa el correo o teléfono proporcionado por el huésped: no se envían correos automáticos desde esta versión.

También puedes crear el administrador desde la terminal:

```powershell
.venv\Scripts\python.exe app.py create-admin
```

La recuperación de contraseña es asistida por recepción, no por correo automático. Tras verificar la identidad del solicitante, el administrador con acceso al servidor puede ejecutar:

```powershell
.venv\Scripts\python.exe app.py reset-password
```

## Qué funciona

- Registro e inicio/cierre de sesión con datos persistentes; cambio de contraseña.
- Acceso inicial con opción de continuar como visitante.
- Búsqueda por fechas y huéspedes; filtros y detalle de habitaciones.
- Precio calculado en el servidor, no confiado al navegador.
- Reservas con código, historial personal, estados y cancelación antes del día de llegada.
- Asignación de unidades mediante transacción SQLite; sin reservas superpuestas para la misma unidad.
- Galería ampliable con controles de teclado y cierre con Escape.
- Reseñas de usuarios con una estancia completada, una por cuenta, moderadas desde recepción. No se inventan reseñas.
- Google Maps integrado, controles de mapa/satélite, enlace para rutas, referencia enviada y copia de dirección. Requiere Internet.
- Formulario de contacto que guarda consultas en el panel.
- Menú móvil, formularios accesibles, foco visible y soporte para movimiento reducido.
- Teléfono fijo publicado en directorio. WhatsApp se muestra solo al configurar un número real en el campo whatsapp.

## Personalizar antes de usar con clientes

Edita **hotel.json** con VS Code. Guarda como UTF-8 y reinicia el servidor.

| Campo | Qué cambiar |
| --- | --- |
| name / tagline | Nombre y frase del hotel |
| city / address | Ciudad y dirección exacta |
| map_query | Dirección o coordenadas para el mapa |
| phone | Teléfono real con prefijo internacional, por ejemplo formato +51 seguido del número |
| email | Correo real de recepción |
| whatsapp | Número móvil real con código de país, solo dígitos; no usar el teléfono fijo |
| checkin / checkout | Horarios reales |
| rooms[].price | Tarifa final en soles por noche |
| rooms[].units | Cantidad de habitaciones físicas de ese tipo |
| rooms[].capacity / beds / size | Capacidad, camas y área reales |
| rooms[].features / description | Servicios y descripción reales |
| rooms[].image | Archivo en static/img |
| demo | Cambiar a false únicamente después de completar todos los datos reales |

Las tarifas S/ 70, 100, 120 y 160 proceden de la primera referencia; S/ 110, 145, 190 y 210 son importes de ejemplo añadidos a petición del usuario. El inventario inicial de dos unidades por tipo es solo de muestra. No cambies los identificadores ni reduzcas unidades cuando ya existan reservas activas; primero resuelve las reservas afectadas.

La portada, textos de ubicación referencial y marca también aparecen en **templates/index.html** y **static/app.js**: revisa estos textos al personalizar para otro negocio. Secciones y textos: index.html. Colores, tamaños y animaciones: static/style.css. Interacciones: static/app.js. Reglas y API: app.py.

La fachada y la captura de ubicación fueron proporcionadas por el usuario. Las imágenes de interiores son ilustraciones fotográficas de referencia generadas para este proyecto, no fotografías de las habitaciones del establecimiento. Sustitúyelas antes de promocionar un hotel real. Las ocho habitaciones son ejemplos ficticios; las imágenes se reutilizan en algunas categorías. La habitación simple admite una persona. Ver CREDITOS.md.

Completa además la identidad del responsable y las condiciones de privacidad/cancelación en la interfaz. La política incluida es un texto de muestra y debe reflejar la operación del hotel.

## Datos y respaldo

El primer inicio genera **instance/hotel.sqlite3** y **instance/secret.key**. El ZIP no contiene usuarios, reservas, contraseñas ni claves de pruebas. Los datos permanecen aunque cierres la aplicación. No borres esta carpeta si deseas conservarlos.

Para respaldar: detén el servidor y copia toda la carpeta instance a un lugar privado. No la publiques, no la incluyas en Git y no la compartas dentro de un ZIP comercial. No guardes la base de datos en una carpeta web pública.

## Seguridad y publicación

Incluye hashes scrypt, consultas parametrizadas, control de acceso en servidor, protección CSRF, cookies HttpOnly/SameSite, límite de solicitudes de acceso, validación de fechas/capacidad, escape de textos y cabeceras de seguridad. No se promete seguridad absoluta: la seguridad en producción también depende del alojamiento y su mantenimiento.

Esta entrega es para ejecutar localmente; no incluye dominio ni despliegue. Para publicar necesitas un servidor que soporte Python, un disco persistente para SQLite, HTTPS y copias de respaldo. Un alojamiento exclusivamente estático no ejecutará el backend. Ejecuta un único proceso de aplicación con su disco local; no uses este SQLite para múltiples servidores sin migrar a una base de datos compartida.

Variables opcionales:
- HOTEL_HTTPS=1: cookies Secure y HSTS. Usar solo detrás de HTTPS real; no activarlo para http://localhost.
- SECRET_KEY: secreto aleatorio propio del servidor. Si se omite, se genera localmente y se guarda con permisos restringidos.
- HOTEL_DATA_DIR: carpeta privada persistente de datos.
- HOST / PORT: dirección y puerto de escucha de app.py (por defecto 127.0.0.1:5000).

Mantén el servicio detrás de un proxy HTTPS, actualiza dependencias y realiza revisión de seguridad antes de recibir datos reales. La limitación de solicitudes usa la IP que recibe la aplicación; si incorporas un proxy, configura correctamente los clientes de confianza antes de modificar este comportamiento.

No hay pasarela de pagos, envío automático de correos, verificación de correo ni sincronización con Booking/Airbnb. Las solicitudes pendientes bloquean la unidad hasta que recepción las confirme o cancele; revísalas regularmente. Las condiciones de pagos externos, impuestos, servicios y políticas deben completarse con el negocio.

## Verificación

El archivo PRUEBAS.md resume las comprobaciones realizadas. Para ejecutar las pruebas de backend desde la carpeta raíz:

```powershell
.venv\Scripts\python.exe tests.py
```


## Cambios de la segunda edición

- Rediseño de la portada, navegación, catálogo, servicios, galería y sección de ubicación.
- Ocho habitaciones de ejemplo con categoría, área, capacidad, camas, descripción y comodidades.
- Búsqueda por nombre/cama/servicio, filtro de capacidad, filtro de comodidades y orden por precio o tamaño.
- Mapa conectado a Google Maps mediante contenido externo; controles de mapa/satélite, recarga, ruta y abrir en Google.
- Copiar dirección, referencia visual aportada por el usuario y enlace a la fuente de dirección.
- Enlace a Google Maps para consultar allí la ficha y reseñas. No se copian reseñas ni se simula una puntuación de Google.
- Barra inferior de acceso a habitaciones y fechas en móvil.
- Cierre de sesiones antiguas al cambiar o restablecer la contraseña, mediante versión de sesión verificada en servidor.
- Fotografías aportadas por el usuario conservadas sin retoques.

### Qué significa la conexión con Google Maps

El mapa se obtiene del servicio de Google al abrir la sección; no es la captura que enviaste. La captura se conserva por separado en «Ver referencia enviada». La información y el resultado de búsqueda dependen de Google. No implica seguimiento GPS, imágenes satelitales tomadas en tiempo real ni acceso automático a sus reseñas. El cálculo de ruta se abre directamente en Google Maps, que puede pedir la ubicación al visitante.

Se usa una búsqueda por nombre y distrito, no un Place ID verificado. Antes de publicar, confirma el pin desde la ficha real y reemplaza map_query si hace falta. La numeración publicada es Av. Alameda 622; otra fuente describe Las Orquídeas con Alameda Marginal. No se encontró una fuente oficial del establecimiento que resolviera esta diferencia.

Estas solicitudes de demostración se guardan en la aplicación local. No se envían al establecimiento real. Para que recepción las gestione en operación, se debe desplegar la aplicación y dar acceso a su personal autorizado, además de cargar inventario, tarifas y datos reales.

### Animación y accesibilidad

Entrada suave de secciones, transición de tarjetas al filtrar, realce del menú de la sección visible, cabecera con sombra al desplazarse y estados visuales de botones. Se respeta la opción del dispositivo «reducir movimiento». No se altera la velocidad de desplazamiento del navegador ni se bloquean los controles durante las animaciones.
