# Versión 7 · Borgoña

Consulta primero CAMBIOS_V7.md. Esta es la versión completa; el catálogo estático se entrega por separado.

# Versión 6 · Ecosistema Sapphire

Lee primero `CAMBIOS_V6.md` para las funciones actuales. Las secciones siguientes incluyen documentación de versiones anteriores.

# Versión 5 · Pagos y administración

- 23 habitaciones numeradas 001–023 (catálogo de ejemplo, una unidad por habitación).
- Tras enviar la solicitud se abre directamente el QR de Yape proporcionado por Enrique, sin alterar su imagen, con botón de descarga.
- El cliente paga dentro de Yape y sube el comprobante JPG/PNG/WebP. La web no lee la clave de Yape ni verifica automáticamente el banco.
- Pago al llegar: registra la elección, genera aviso a recepción y permanece pendiente de aprobación. No cuenta como ingreso hasta que recepción registra el dinero recibido.
- Admi abre /admin, una página independiente con menú, ingresos por período, gráfico de 14 días, clientes con DNI, reservas, comprobantes y habitaciones.
- Comprobantes privados en instance/receipts. Guardar esa carpeta en las copias de seguridad. No se sirven por /static.
- WhatsApp automático: requiere credenciales de Business y ejecutar enviar_avisos.py periódicamente. La plantilla aprobada ahora necesita 8 parámetros: código, evento, nombre, monto, ingreso, salida, habitación, DNI. El botón manual abre el texto, pero requiere pulsar Enviar dentro de WhatsApp. No se enviaron mensajes durante las pruebas.
- No se implementa un enlace no documentado para abrir Yape con destinatario precargado. Descarga el QR y cárgalo desde Escanear QR en la app. Fuente oficial: https://www.yape.com.pe/preguntas-frecuentes/enviar-y-recibir-yapeos/30--donde-encuentro-mi-qr
- Las nuevas habitaciones no corresponden a un inventario confirmado del hospedaje. Extrae en otra carpeta para probar. Si necesitas conservar reservas antiguas, respalda instance y revisa las antiguas unidades 2 antes de migrar: el catálogo nuevo representa habitaciones individuales.
- Los paneles de reservas y clientes muestran las últimas 500 reservas; los totales monetarios se calculan sobre todos los pagos aprobados. No se descuentan automáticamente los reembolsos.
- La prueba vigente de esta versión es test_v5.py; test_v4.py y los informes anteriores son históricos.

# Correcciones 4.1

Cabecera clara al desplazarse, sin franja de vista previa en portada y sin botón Google cuando no está configurado. Live Server no solicita contraseñas: el acceso dirige a las instrucciones de la web completa. Consulta ABRIR_LA_WEB.txt.

# Hospedaje Río Negro · versión 4

## Ver el diseño con Live Server

Abre la carpeta **hospedaje-rio-negro** en VS Code y abre el archivo **index.html de la raíz** con Live Server. No abras templates/index.html: esa plantilla la interpreta Python.
La vista previa incluye catálogo, galería, navegación, animaciones y mapa. La portada no muestra avisos técnicos. Al pedir acceso se explica cómo abrir la web completa; este modo no crea cuentas ni guarda reservas. Nunca introduce cuentas falsas ni pagos simulados como reales.

## Usar cuentas, reservas, administración y pagos informados

Extrae el ZIP. Dentro de la carpeta que contiene requirements.txt, pulsa Ctrl+L en el Explorador, escribe cmd y pulsa Enter. Ejecuta cada línea por separado:

```bat
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe preparar_demo.py
.venv\Scripts\python.exe iniciar.py
```

Abre http://127.0.0.1:5000 y deja la consola abierta.
La inicialización de prueba crea **pruebaht@gmail.com**, contraseña **132007**, solo si esa cuenta no existe. Debes cambiarla al entrar antes de poder administrar. No se crea automáticamente en un despliegue. No uses esta contraseña pública en producción.
En Admi → Mi cuenta puedes cambiar correo y contraseña. Para una instalación real usa `python app.py create-admin`, sin ejecutar preparar_demo.py.

## Cambiar tus fotos y logo

Opción sencilla: entra como administrador → **Admi → Cambiar fotos**. Selecciona portada, logo, fachada, QR oficial o habitación. Admite JPG, PNG y WebP hasta 5 MB / 20 megapíxeles, y reescribe la imagen para descartar contenido extra. Solo administradores pueden cargar archivos.

Desde VS Code: coloca tus imágenes en **static/img/**. En **hotel.json**, edita:
- `logo`: nombre de archivo del logo.
- `hero`: portada e imagen del acceso.
- `facade`: primera foto de galería.
- `rooms`: `image`, `name`, `description`, `price`, `capacity`, `units` y servicios de cada habitación.
- `yape_qr`: archivo del QR REAL descargado de tu propia aplicación Yape. Vacío significa pendiente.

Usa nombres de archivo simples, sin rutas externas. Para actualizar también la vista de Live Server tras un cambio, ejecuta `.venv\Scripts\python.exe crear_vista_previa.py`. En la web con Python las imágenes del panel se actualizan al recargar. Las imágenes y la configuración deben persistir en el hosting; no mantenerlas solo en un contenedor efímero.

## Flujo de reserva y pago

Desde v6 el titular introduce DNI, sin fecha de nacimiento. Se valida el formato, **no la identidad oficial**. El DNI no se publica. Recepción tiene que verificar el documento original y la mayoría de edad antes de aprobar. RENIEC requiere un acceso autorizado y no está conectado en esta entrega.

1. El cliente crea una solicitud con fechas y teléfono.
2. Ve el monto, el número Yape configurado y, si se cargó, el QR oficial descargable.
3. Tras pagar, informa el número de operación; estado **en revisión**.
4. El administrador comprueba el dinero en su propia cuenta y el documento del huésped, y aprueba el pago.
5. Después confirma la reserva. El servidor bloquea confirmaciones sin pago aprobado.

Una referencia de operación o una captura no acredita el pago. No hay verificación bancaria automática. Los campos BCP / Interbank son muestras claramente marcadas y no aceptan pagos. No se recopilan números de tarjetas ni CVV. Los ingresos se calculan sobre pagos aprobados según fecha de aprobación en Lima, sin descontar reembolsos. Cancelar no devuelve dinero automáticamente; el reembolso se gestiona fuera del sistema.

El QR personal de Yape puede pedir al pagador introducir el monto. Esta versión no crea QR dinámicos con monto garantizado. Fuente: https://www.yape.com.pe/preguntas-frecuentes/enviar-y-recibir-yapeos/31--como-hago-un-pago-con-qr

## Google, RENIEC y WhatsApp

**Google:** se incluyó el flujo OAuth con Authlib. Configura en el servidor `GOOGLE_CLIENT_ID` y `GOOGLE_CLIENT_SECRET`, y registra como retorno `https://TU-DOMINIO/auth/google/callback` (en local, http://127.0.0.1:5000/auth/google/callback). El acceso pide autorización y valida correo verificado. No se probó con credenciales reales. Las cuentas administrativas usan contraseña local para evitar cambios de permisos por coincidencia de correo. Fuente: https://docs.authlib.org/en/latest/oauth2/client/web/flask.html

**RENIEC:** NO hay conexión activada ni implementada contra un servicio privado no autorizado. Se requiere contratar/obtener acceso oficial, conocer su interfaz y sus condiciones antes de conectar. El formato del DNI o la fecha declarada no verifica identidad. Fuente: https://www.gob.pe/13543

**WhatsApp:** el botón de consulta abre el chat al 939017959 con código e importe. Además, existe una cola transaccional para solicitudes, pagos informados y pagos aprobados. No se envió ningún mensaje durante las pruebas. Para envío automático, configura un número emisor en WhatsApp Business Cloud API y una plantilla aprobada de 8 parámetros: código, evento, nombre, monto, ingreso, salida, habitación, DNI. Variables: `WHATSAPP_TOKEN`, `WHATSAPP_PHONE_ID`, `WHATSAPP_TEMPLATE`, `WHATSAPP_API_VERSION`, `WHATSAPP_LANGUAGE` (por defecto es_PE). Configura la versión activa de tu aplicación Meta. Programa `python enviar_avisos.py` cada minuto en el servidor con esas variables. Destino fijo: 51939017959. Se envía DNI para identificar al cliente en recepción; nunca contraseña ni tarjeta. Los datos restantes se consultan en el panel protegido.

La cola distingue pendiente, enviando, aceptado por Meta, fallido e incierto. Aceptado no significa entregado. Una interrupción puede dejar estado enviando; revisar antes de reintentar para evitar duplicados. Esta versión no incorpora webhooks de entrega ni reintentos automáticos de estados inciertos. Fuente: https://whatsapp.github.io/WhatsApp-Nodejs-SDK/api-reference/messages/template/

## Seguridad y publicación

Contraseñas con hash, CSRF, cookies HttpOnly/SameSite, consultas parametrizadas, control de roles, límites de intentos, cambios de contraseña que invalidan sesiones y validación de imágenes. Cuenta de prueba exige cambiar contraseña. El navegador nunca decide los permisos ni el importe final. No se promete invulnerabilidad.

Antes de publicar: HTTPS, claves privadas fuera del código, cuenta administrativa privada, política de privacidad completada por el hospedaje, copia de seguridad y límites de conservación de DNI. Las políticas incluidas siguen siendo un modelo pendiente de personalización. SQLite es para pruebas locales; PostgreSQL y nginx están preparados pero no probados aquí. No hay garantía de capacidad ilimitada. Prueba carga en tu hosting y configura persistencia compartida de las imágenes y hotel.json. La configuración de fotos utiliza bloqueo de archivo y reemplazo atómico. Compose incorpora volúmenes para las imágenes y configuración; comprueba permisos, copias y restauración en el servidor. Para Google y WhatsApp añade sus variables al servicio web / tarea de avisos: no se inyectan automáticamente por existir en .env.

## Comprobación

`python test_v4.py` verifica autorización, CSRF, edad declarada, reserva idempotente, pago informado, aprobación, confirmación bloqueada antes del pago, métricas, rechazo de archivos inválidos y cambios de cuenta.


## Seguridad v11
La base SQLite y los comprobantes se almacenan fuera de `/static` y no tienen rutas HTTP públicas. Para producción define `HOTEL_DATA_DIR` en una carpeta privada fuera de la raíz pública y usa PostgreSQL mediante `DATABASE_URL`. No publiques el directorio completo del proyecto con otro servidor web.
