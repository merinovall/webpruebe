> VERSIÓN 4: lee primero LEEME_PRIMERO.md. Este documento conserva información y pruebas de la versión 3; no certifica las nuevas integraciones.

# Verificación de la entrega

Pruebas ejecutadas en un entorno aislado, sin incluir sus usuarios ni datos en el ZIP.

## Servidor — aprobado

- Registro e inicio de sesión; cambio de contraseña.
- Rechazo de peticiones de escritura sin token CSRF.
- Rechazo de acceso no autorizado al panel de recepción.
- Separación de las reservas entre diferentes cuentas.
- Cálculo de importe en servidor aunque el navegador envíe otro precio.
- Fechas y capacidad inválidas rechazadas.
- Límite de unidades disponibles, rechazo al agotar inventario y liberación tras cancelar.
- Rechazo de cancelación por un usuario ajeno a la reserva.
- Formulario de contacto guardado.
- Reseña rechazada sin estancia completada; publicación después de moderación.
- Cabecera de política de seguridad de contenido presente.

## Navegador Chromium — aprobado

- Recursos locales cargados y sin errores de JavaScript durante el recorrido probado.
- Apertura/cierre de ventanas y filtros de habitaciones.
- Galería ampliable y navegación entre fotografías.
- Registro desde la interfaz.
- Búsqueda por fechas, reserva y cancelación desde la interfaz.
- Envío de consulta desde el formulario.
- Anchos 320, 390, 768, 1024 y 1440 píxeles, sin desplazamiento horizontal inesperado.
- Inspección visual de la página en escritorio y móvil.

## Alcance

No equivale a una auditoría de seguridad ni garantiza ausencia absoluta de fallos. No se probó en cada dispositivo físico, Safari o Firefox. Google Maps y los enlaces de contacto externos dependen de Internet y de datos reales del hotel; la carga del mapa externo no pudo verificarse en este entorno. No se han desplegado servicios de pagos, correo o dominio. El iniciador Windows se entrega con instrucciones; las pruebas se ejecutaron en Linux/Python y Chromium.


## Segunda edición — verificaciones adicionales

Servidor: suite de integración superada después de incorporar la versión de sesión.
Navegador: filtros de ocho habitaciones, búsqueda por texto, filtro por escritorio y orden descendente por precio superados. Recorrido de registro, disponibilidad, reserva, cancelación y contacto repetido sin errores JavaScript. Verificados anchos de 320, 390, 768, 1024 y 1440 píxeles sin desbordamiento horizontal.

Google Maps: la aplicación usa la URL del servicio y enlaces de ruta/ficha. Su contenido externo requiere Internet y no se puede garantizar ni verificar el pin exacto desde este entorno. La dirección publicada y el contacto necesitan confirmación del establecimiento.


## Edición Astral

Flujo funcional y navegador: superados después del rediseño y de añadir claves de solicitud. Ensayo HTTP concurrente: consultar RESULTADO_CARGA.json y DEPLOY_Y_CAPACIDAD.md. PostgreSQL, Docker y Nginx no se ejecutaron en este entorno; su configuración necesita validación en destino.

## Corrección v3.1

Corregido el ancho del texto de portada: el margen exterior ya no se resta del ancho disponible del contenido. Verificado en Chromium a 320, 390, 768, 1024, 1440, 1920, 2048, 2560 y 3440 píxeles. Las etiquetas {{ hotel.name }} se procesan iniciando Python, no abriendo templates/index.html con Live Server.
