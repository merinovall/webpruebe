# Pruebas versión 5

Backend SQLite: 23 habitaciones 001–023; acceso administrativo; reserva con pago al llegar; idempotencia de esa elección; ingresos excluyen pagos no recibidos; aprobación de reserva con verificación documental; recepción del dinero; captura válida e inválida; acceso privado a comprobantes; usuarios ajenos y visitantes rechazados; aprobación de Yape; totales y eventos WhatsApp con DNI. Ejecutar python test_v5.py.

Chromium: catálogo de 23 tarjetas; registro; solicitud abre el QR automáticamente; carga de comprobante; navegación a /admin; aprobación del pago y de la reserva; menús de clientes, habitaciones, reseñas, informes y cuenta; sin errores JavaScript. Administración verificada entre 320 y 1440 px, sin desbordamiento horizontal.

Pruebas usan datos ficticios y bases temporales. No se enviaron pagos ni WhatsApp reales. Google, Meta y PostgreSQL no se verificaron contra servicios reales. QR incluido sin alteración según imagen del usuario: no se ejecutó un pago para comprobar el destino.
