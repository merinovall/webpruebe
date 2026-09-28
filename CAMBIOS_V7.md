# Web completa · v7 Borgoña

Nueva paleta: #380F17, #8F0B13, #EFDFC5, #252B2B y #4C4F54. Cabecera de dos niveles en escritorio, menú compacto en móvil, tarjetas con reflejos y panel de administración con la misma paleta. Transición animada entre ingreso y registro, respetando movimiento reducido.

Se retiraron el texto «Escenario conceptual generado…» y el control visible del video. El video continúa en silencio y bucle; se detiene fuera de pantalla o con la pestaña oculta. Si el dispositivo solicita movimiento reducido o no permite reproducción automática, queda la imagen de respaldo. Coloca mi-video.mp4 en static/video/; el video no viene incluido.

El número de operación del comprobante es opcional. La imagen sigue siendo obligatoria y el pago continúa sujeto a verificación manual del abono real.

Los usuarios registrados pueden enviar una reseña sin tener una estancia completada. Se mantiene una reseña por cuenta y moderación antes de publicación.

El catálogo consulta disponibilidad al abrirse, al cambiar fechas y cada 15 segundos mientras la pestaña está visible. Las habitaciones sin cupo muestran «🔒 Ocupada» y el botón queda desactivado. Se bloquean para el intervalo de fechas elegido, no permanentemente. El servidor vuelve a comprobar el inventario al reservar para evitar dobles reservas. Las reservas pendientes también bloquean el cuarto; el plazo de una hora para pago al llegar sigue vigente.

Los números no se envían al público en bootstrap, disponibilidad ni en los datos de vista previa. Los identificadores del catálogo son opacos; nombres y descripciones públicos eliminan el prefijo numérico y la referencia estructurada al piso de los ejemplos. La numeración se devuelve al titular en Mi estancia, y el administrador ve la configuración completa. No escribas números privados dentro de textos comerciales o imágenes: esos contenidos son públicos. El informe de llegada completo conserva el requisito de pago y reserva confirmados.

Prueba test_v7.py: privacidad del catálogo, número solo en reserva propia, reseña antes de estancia, comprobante sin referencia, bloqueo de inventario y liberación al cancelar. Prueba de navegador: registro, carga de comprobante sin referencia, bloqueo del botón, panel, editor y adaptación de 320 a 1440 píxeles.

Abrir: sigue ABRIR_LA_WEB.txt. Live Server es una vista visual; la disponibilidad real, edición, cuentas y pagos necesitan iniciar.py. El catálogo independiente no se modificó.

RENIEC, Google y WhatsApp automático siguen requiriendo acceso y credenciales oficiales. No se han realizado consultas a RENIEC ni verificación bancaria automática. No se ha ejecutado una auditoría de seguridad ni una prueba de carga de esta versión.
