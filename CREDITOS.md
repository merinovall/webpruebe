# Diseño y recursos

Referencia de estructura: https://hotelmayros.com/ (consultada durante la elaboración).
Referencia visual: imagen aportada por el usuario, «Hotel Sol Andino».
Implementación original con tipografía Arial/Helvetica/sans-serif del sistema. No se distribuyen archivos de fuentes ni recursos de Hotel Mayros.

Imágenes: generadas mediante la herramienta integrada ImageGen para este proyecto. Ilustraciones fotográficas, no documentación de un hotel real. Prompts: interiores de hotel en formato horizontal, madera de nogal, ropa de cama crema, luz natural, sin personas, logos ni texto; una habitación king, una twin con dos camas separadas y una familiar con cama doble y dos individuales. Archivos: static/img/room1.png y room3.png (king reutilizada), room2.png (twin), room4.png (familiar).

Mapa: servicio externo Google Maps, con sus propias condiciones. Se necesita conexión a Internet.
Código de interfaz y servidor creado para EMB MERVAL. Flask, Werkzeug y Waitress conservan sus respectivas licencias de software de terceros; se instalan como dependencias y no se redistribuyen en este ZIP.


## Segunda edición: Hospedaje Río Negro

Fachada y captura de ubicación: imágenes aportadas por el usuario para esta edición. La captura de mapa es una referencia estática, separada del mapa embebido de Google. No se afirma titularidad de las marcas o imágenes de Google.

Dirección y teléfono publicados consultados:
- https://www.deperu.com/comercios/hospedajes/hospedaje-rio-negro-16193 — Av. Alameda 622; teléfono (064) 549128. Son datos de un directorio, sin confirmación de vigencia por el propietario.
- https://www.perutoptours.com/index11ju_directorio_hh.html — referencia alternativa: Las Orquídeas y Alameda Marginal. Confirmar numeración antes de publicar.

Las ocho categorías de habitación, su equipamiento y precios son ejemplos de diseño a petición del usuario, no un catálogo verificado del establecimiento. El diseño no es el sitio oficial del hospedaje.


## Edición Astral

Portada: static/img/astral-hotel.png, generada con ImageGen integrado. Prompt: refugio tropical minimalista de noche junto a agua tranquila, vegetación esmeralda a la derecha, ventanas cálidas, cielo estrellado y luna fina, lado izquierdo oscuro para texto; sin logotipos, textos ni interfaz. Es una escena imaginaria, no una fotografía del Hospedaje Río Negro.

Referencia visual del usuario: estilo minimalista oscuro natural, reinterpretado con diseño, contenidos y recursos originales.


## V8 · Seguridad y UX

La barra superior y la paleta azul marino/crema/dorado se rediseñaron a partir de la imagen de referencia aportada por el usuario. La referencia se usa únicamente como guía visual; no se reutilizan su marca, textos, fotografías ni código.

Se reforzaron cabeceras HTTP de seguridad, la protección de sesión/CSRF existente y la experiencia de acceso. Estas medidas no sustituyen una revisión legal o una auditoría de seguridad antes de publicar.
