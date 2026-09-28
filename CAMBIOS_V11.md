# Hospedaje Río Negro — v11

- Corregido el scroll interno del formulario de reserva para pantallas pequeñas.
- El estado Reservada ya no muestra emoji de candado ni cursor/indicador de espera.
- La actualización automática de disponibilidad ya no vuelve a renderizar las habitaciones si nada cambió, evitando el destello visual periódico.
- Panel de administración alineado con la paleta borgoña actual.
- Reservas y pagos muestra un contador circular de solicitudes nuevas y lo marca como leído al entrar.
- Las confirmaciones de pago, aprobación y liberación usan una ventana modal propia.
- Se eliminó la acción visible Cancelar; ahora el administrador dispone de Libre, que conserva el historial y libera la habitación.
- Las expiraciones automáticas pasan a Libre.
- Se eliminó del pie del panel la frase sobre datos reales/zona horaria.
- Se mantienen CSRF, cookies protegidas, consultas parametrizadas, CSP y almacenamiento de base/comprobantes fuera de /static.
