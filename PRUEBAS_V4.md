# Validación versión 4

Pruebas locales con SQLite: CSRF, permisos administrativos, edad declarada, idempotencia de reserva, pago informado, aprobación manual, confirmación condicionada al pago, métricas de ingresos, protección de reservas ajenas, carga válida e inválida de imágenes, cambio de correo y contraseña.

Navegador Chromium: anchuras 320, 390, 768, 1024 y 1440; sin desbordamiento horizontal, recursos gráficos cargados, filtros, galería, registro, búsqueda, reserva, pago informado y cancelación sin errores JavaScript. Acceso administrativo, cambio obligatorio de contraseña inicial, métricas y formulario de imágenes comprobados. Vista estática equivalente a Live Server comprobada.

No se han probado con servicios reales: Google OAuth, WhatsApp Cloud API, pagos bancarios, RENIEC. No se enviaron mensajes ni pagos. No se probó Docker/PostgreSQL ni carga de producción. Los resultados de carga históricos pertenecen a la versión anterior.

Versión 4.1: verificado fondo claro de cabecera después del desplazamiento en 320, 390, 768 y 1440 px; eliminada franja de portada; Google oculto sin configuración; Live Server no presenta campos de contraseña. Comprobado en servidor estático y Flask.
