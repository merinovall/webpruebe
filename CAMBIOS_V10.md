# v10 — acceso, reservas y privacidad de números

- El cuadro de inicio de sesión es exclusivamente un `<dialog>` modal centrado; no ocupa espacio en la página de inicio.
- Si el visitante no tiene sesión, el acceso se abre al cargar la web. Puede cerrarlo y navegar; vuelve a aparecer al recargar.
- Al intentar reservar sin sesión, se abre el mismo acceso y, tras iniciar sesión, continúa con la reserva.
- La cabecera permanece transparente sobre la portada y mantiene un desenfoque discreto al desplazarse.
- Una habitación sin unidades disponibles se muestra como `Reservada` y el botón queda deshabilitado.
- El backend ya bloquea la reserva cuando todas las unidades están ocupadas para esas fechas; la comprobación se repite en el servidor al enviar la reserva.
- Los números internos de habitación no se incluyen en el catálogo público ni en `/api/availability` para visitantes.
- El panel de administración conserva los números internos.
- El cliente solo recibe el número asignado cuando su propia reserva está confirmada y el pago está aprobado, mediante su información privada de estancia.
