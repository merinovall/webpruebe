# Hospedaje Río Negro · v6

## Diseño y edición

Paleta de la referencia: Sapphire #3C507D, Royal Blue #112250, Quicksand #E0C58F, Swan Wing #F5F0E9 y Shellstone #D9CBC2. Arial en toda la web. Menú flotante sólido, tarjetas, panel y formularios adaptados a móvil. Se mantiene el fondo de video: copia tu archivo a `static/video/mi-video.mp4`. El MP4 no está incluido.

En **Admi → Habitaciones → Editar habitación** puedes cambiar las 23 habitaciones: nombre, número único, precio por noche (soles enteros), capacidad de 1 a 4, superficie, categoría, camas, servicios, descripción, piso, lado, ventana e indicaciones. Puedes desactivar nuevas reservas sin borrar las antiguas. Cambia la fotografía desde el mismo editor. Los pisos, lados y vistas incluidos son ejemplos: reemplázalos por los datos reales antes de aceptar huéspedes.

En **Admi → Configuración** puedes cambiar nombre, subtítulo, dirección, ciudad, teléfono, WhatsApp de contacto, horas de ingreso/salida y textos de portada/presentación. También logo, fachada, portada, QR y fotos de habitaciones. La galería usa la fachada y las habitaciones 002–004. Los cambios se guardan en el servidor, sin editar código. No es un editor visual de todas las secciones: la estructura, las políticas y los textos secundarios se editan en las plantillas.

Las reservas conservan su importe original. El informe conserva la información de habitación tomada al confirmar, aunque después edites el catálogo. Las modificaciones de configuración son atómicas, pero ante dos administradores editando el mismo cuarto prevalece el último guardado.

## Una hora para pagar al llegar

El plazo empieza **al pulsar «Reservar y pagar al llegar»**, incluso para una fecha futura. Se informa antes de elegir y se muestra la hora límite de Lima. Repetir el botón no renueva el plazo. La reserva se cancela si no tiene pago aprobado dentro de los 60 minutos, aunque ya estuviera confirmada. Subir una captura no extiende el plazo: recepción debe comprobar el dinero. Una captura que llegue después del vencimiento no reactiva una reserva; si hubo un abono tardío, recepción debe resolverlo con el cliente.

El reloj se controla en el servidor. El inicio normal por `iniciar.py` o `app.py` procesa vencimientos cada 15 segundos. Las APIs también los procesan antes de consultar disponibilidad o modificar reservas. Gunicorn incluye el mismo trabajador por proceso. Si el servidor está apagado no ejecuta tareas; al reiniciar o en la siguiente consulta procesa lo vencido. No se depende del navegador del huésped.

El diálogo de pago se cierra al guardar un comprobante o elegir pago al llegar. La portada muestra el estado actualizado (consulta cada 15 segundos mientras está abierta). El usuario puede abrir Mi estancia para revisar la reserva activa. Las canceladas, completadas o con fecha de salida ya alcanzada no aparecen en su lista; permanecen en administración para reportes. No se borran del registro contable.

## Informe de llegada

Cuando recepción ha confirmado **tanto el pago como la reserva**, el cliente ve su informe en la web y puede descargarlo como TXT: dirección, habitación, número, piso, lado, ventana, camas, servicios e indicaciones. Es privado y solo lo descarga el titular con una reserva activa. El aviso es dentro de la web, no un correo ni un WhatsApp automático al huésped.

## Identidad

Se eliminó la fecha de nacimiento del formulario. El estado de revisión documental solo aparece en administración. No hay consulta automática a RENIEC: requiere convenio, credenciales y documentación del servicio autorizado. No se simula una respuesta oficial. Por ahora, recepción confirma explícitamente que revisó el documento original y la mayoría de edad al aprobar una reserva.
Referencia oficial: https://www.gob.pe/13543

## Pagos y conexiones

El QR de Yape se mantiene como imagen proporcionada. El pago se verifica manualmente contra el abono real, no por la apariencia de una captura. WhatsApp automático a recepción y Google siguen necesitando sus credenciales; no se enviaron mensajes ni se efectuaron cobros durante las pruebas. Los avisos a recepción mantienen el destino previamente establecido, 939017959; el WhatsApp editable en Configuración es el contacto público. El mapa sigue usando Google Maps con la dirección configurada.

## Abrir y actualizar

Extrae en una carpeta nueva. Dentro de la carpeta que contiene `iniciar.py`, pulsa Ctrl+L, escribe `cmd` y presiona Enter. Sigue `ABRIR_LA_WEB.txt`. Live Server sirve la vista visual; cuentas, edición, pagos y reservas necesitan el servidor Python.

Si ya tienes datos: haz copia de seguridad de tu carpeta anterior; preserva `instance/`, tus imágenes subidas, video y configuración personalizada. La migración SQLite añade columnas y no borra clientes. Si conservas un hotel.json anterior, revisa y completa los nuevos campos desde Admi antes de confirmar reservas. PostgreSQL requiere volver a aplicar `schema_postgres.sql` antes de arrancar. No se ha probado PostgreSQL ni Docker en esta entrega.

Tras cambios desde el panel, recarga la web para verlos. Para actualizar también la copia estática de Live Server, ejecuta `python crear_vista_previa.py`.

## Verificado

- Prueba de integración v5: QR/comprobante, privacidad de archivos, aprobación e ingresos.
- Prueba v6: límite de una hora sin renovación, cancelación y liberación del cuarto, pago aprobado protegido, informes privados, datos internos ocultos, historial fuera de la vista del cliente, edición protegida, precios inválidos/números duplicados rechazados y conservación del importe e informe originales.
- Navegador Chromium: registro sin nacimiento, 23 habitaciones, envío y cierre automático del diálogo, Admi separado, revisión y confirmación, edición de precio/piso/textos, navegación del panel y diseño de 320 a 1440 px sin desbordamiento horizontal.
- Sin ensayo de carga de esta versión, auditoría completa de seguridad ni conexión a RENIEC/bancos/Google/Meta. Ningún servidor tiene capacidad ilimitada.

Las capturas de `VISTAS_PREVIAS` contienen datos ficticios de prueba. El ZIP no contiene base de datos de clientes, sesiones ni secretos del entorno de pruebas.
