---
name: "creadora-apps-web-pwa"
description: "Diseña, construye, prueba, despliega y entrega apps web PWA para cualquier rubro (reservas, pagos, fidelización, notificaciones), con stack abierto, VPS+Docker y manuales por rol."
---

# Creadora de apps web PWA (agnóstica de rubro y de stack)

Tono: español formal, estructurado, orientado a resultados. Guía paso a paso cuando se configure una plataforma. Nunca inventes capacidades: si algo no se puede automatizar o verificar, dilo.

**Principio rector.** Esta skill define un MÉTODO, no una tecnología. El caso real de referencia (Barbería The Mesías: Next.js 16 + Supabase + Docker + EasyPanel) sirve para extraer patrones, decisiones y errores; NO es plantilla obligatoria. Stack, modelo de datos, roles y funciones se deciden en cada proyecto según rubro, cliente y presupuesto.

## Reglas de trabajo con el usuario
- El usuario pega sus propias claves. Nunca las pidas por chat para guardarlas ni las incluyas en archivos; `.env.example` lleva solo nombres.
- **Avisar antes de actuar** en paneles externos (hosting, base de datos, DNS, GitHub) y esperar confirmación.
- Trabajar por fases, mostrar avances y separar siempre: qué está hecho, qué falta y qué depende del cliente.
- Verificar con evidencia (build real, pruebas, sitio desplegado) antes de afirmar que algo funciona. Declarar lo no verificado.

## Flujo general (7 etapas)
1. Descubrimiento → 2. Arquitectura → 3. Construcción por fases → 4. Pruebas → 5. Despliegue → 6. Entrega de código → 7. Documentación.
Cada etapa termina con un resumen corto al usuario y, si hay decisiones abiertas, una pregunta concreta (preferible con opciones).

### 1. Descubrimiento del negocio
Relevar, preguntando solo lo que no se pueda asumir con seguridad:
- Rubro, usuarios y roles (cliente final, personal operativo, administrador, otros).
- Procesos clave y reglas: precios, cancelaciones/reprogramaciones, pagos (adelanto, saldo, pago total), fidelización.
- Integraciones: WhatsApp, correo, pasarela de pago, Google (login, reseñas), mapas.
- Datos que aportará el cliente: marca, catálogo, horarios, equipo, cuentas de pago, dominio.
- Aclarar **quién cobra y a qué cuenta** y **quién ve qué**. En el caso real el modelo de pagos se reescribió tres veces por asumirlo; confirmar antes de construir y dejar las suposiciones escritas.
- Presupuesto, hospedaje disponible, equipo técnico del cliente, plazo.

### 2. Arquitectura (decisión razonada, no impuesta)
Proponer UNA opción recomendada con justificación y alternativas. Criterios: costo, hospedaje disponible, capacidades del equipo del cliente, escalabilidad, tiempo de entrega, mantenimiento.
- Frameworks web: Next.js, Nuxt, SvelteKit, Remix, Astro u otro adecuado.
- Backend: Supabase (rápido; Auth+RLS+Storage), Firebase, Postgres propio con API a medida, Supabase autoalojado en el VPS (más control, más operación).
- Pagos, autenticación, almacenamiento, correo y mensajería según integraciones.
- Documentar: modelo de datos, roles/permisos, flujos críticos, notificaciones, despliegue.
- Mapa de decisión rápido: sin DevOps en el cliente → servicio gestionado; cliente con VPS propio → Docker + panel; prototipo de bajo costo → Vercel/Railway.

### 3. Construcción por fases
- Fase A (núcleo): autenticación y roles, catálogo, flujo principal (p. ej. reserva), pagos básicos, panel administrativo mínimo, PWA.
- Fase B (extras): fidelización, notificaciones multicanal, push, reseñas, animaciones, estadísticas.
- Entregar cada fase usable. Crear lista de tareas y marcarla al avanzar.
- Seguridad: nunca solo en la interfaz; se aplica en base de datos o servidor.

### 4. Pruebas
- Pruebas automáticas de la lógica crítica (reservas sin solapes, pagos, puntos, canjes, estados, permisos por rol). En el caso real: SQL contra una Postgres temporal con un `run.sh`.
- Compilación limpia: ejecutar el **build real**, no solo el chequeo de tipos.
- Humo en el entorno real tras desplegar (rutas públicas 200, login, flujo principal).

### 5. Despliegue
- Empaquetar con **Docker** (multi-stage, usuario no root, HEALTHCHECK, salida `standalone` si el framework lo soporta).
- Opción por defecto: **VPS con panel tipo EasyPanel** (referencia: Hostinger + EasyPanel + Traefik) con dominio y HTTPS. Alternativas: Vercel, Railway, contenedores propios con docker-compose + Caddy.
- Para Next.js + Supabase en EasyPanel, **invocar o seguir la skill `desplegar-nextjs-easypanel`** (pasos, Google OAuth, primer admin, migración de VPS). Para otros frameworks aplicar los mismos principios cambiando comandos de build/arranque.
- Variables: las públicas del navegador (`NEXT_PUBLIC_*` o equivalente) se **incrustan al compilar** → build args; cambiarlas exige reimplementar. Las secretas solo en ejecución.
- **Regla crítica de redirecciones:** detrás de un proxy inverso, construir toda redirección con una variable de URL pública (`SITE_URL`), NUNCA con `request.url`/`request.nextUrl.origin` (en contenedor valen `0.0.0.0:3000`). Aplica a callback de auth, cierre de sesión y middleware/proxy.
- Servicio separado para cron con su secreto (ver patrón de tareas programadas).
- Endpoint `/api/health` excluido de la autenticación.
- **Migración a otro VPS/dominio:** DNS, recrear app+cron+variables, cambiar `SITE_URL` y reimplementar, actualizar dominios autorizados y URLs de retorno en autenticación/OAuth, verificar dominio de correo (SPF/DKIM), apagar el VPS viejo solo tras probar todo.

### 6. Entrega de código
Preferir commits y PR directos si hay credenciales de Git. Si no las hay (flujo comprobado):
1. Claude construye y prueba (pruebas + build).
2. Entrega un ZIP incremental (solo archivos nuevos/modificados) o completo. **Sincronizar antes de empaquetar** (un archivo local desactualizado puede pisar una corrección).
3. El usuario lo descarga y lo sube al chat.
4. Claude lo sube al repositorio de GitHub y lo extrae con un flujo de GitHub Actions (`extraer-zip`). Verificar que el ZIP esté en el repo antes de ejecutarlo; el ZIP debe tener la carpeta raíz que el flujo espera; eliminar el flujo cuando ya no haga falta.
5. Redespliegue («Implementar» en EasyPanel), **avisando antes**. Aplicar migraciones de BD antes o junto con el código que las usa.
6. Verificar en el sitio real y actualizar manuales.
Si el usuario devuelve una versión editada por él, comparar con `diff` contra la entregada y tomarla como nueva base.

### 7. Documentación y entregables
- App funcional y desplegada; repositorio con migraciones, pruebas y README de despliegue.
- `.env.example` (solo nombres de variables).
- **Manuales de uso por rol** (administrador, personal operativo, cliente final).
- **Documento de alcance**: hecho, pendiente (marcando lo que requiere datos del cliente) y pruebas por hacer. Guardarlo también en el Project si la sesión está vinculada a uno.
- Lista clara de credenciales y datos que debe aportar el cliente (correo, WhatsApp, dominio, pagos).

## Catálogo de patrones reutilizables (cada proyecto elige cuáles usar)

**Roles y accesos.** Cliente / personal / administrador con permisos separados; el personal ve solo lo suyo. Seguridad por filas (RLS) o autorización en servidor. Primer admin asignado por SQL.

**Lógica crítica en servidor.** Reglas sensibles (reservas, pagos, puntos, canjes, estados) en funciones o endpoints protegidos, **idempotentes**. Restricciones de integridad en BD (p. ej. exclusión de solapes). Registros inmutables (libros de movimientos) con triggers. Probar antes de cada entrega.

**Reservas y agenda.** Disponibilidad por horarios y turnos, bloqueo temporal sin pagar que expira solo, cancelación y reprogramación con ventanas configurables, modo «atención en el momento» (sin recordatorios) cuando aplique.

**Pagos.** Manuales (Yape/Plin/transferencia) con número de operación y comprobante, validados por personal o admin; la app **registra**, no mueve dinero, salvo que se integre pasarela. Pasarela con tarjeta (Mercado Pago, Culqi u otras) cuando el cliente aporte credenciales. Esquemas adelanto+saldo o pago total, configurables; destinatario del pago (negocio vs. profesional) explícito; datos de cobro visibles solo al pagador y al personal autorizado; incentivo opcional por subir comprobante.

**Fidelización.** Puntos/estrellas por acciones (bienvenida, visitas, referidos, reseñas, cumpleaños), niveles, catálogo de recompensas, canjes con código; reglas editables por el admin sin tocar código; idempotencia por cita o por periodo.

**Notificaciones multicanal.** Cola con canal (app, correo, WhatsApp), estado, reintentos y claves anti-duplicado. Recordatorios previos (p. ej. 24 h/5 h/30 min), retorno tras visita, promociones, reseñas. Aclarar siempre quién envía: la BD encola con hora programada, el cron despacha, el canal (WhatsApp/correo) solo entrega. Push real con Web Push (VAPID); en iPhone exige instalar la PWA. Aviso por cercanía solo con la app abierta, con permiso y sin guardar la ubicación. WhatsApp: plantillas aprobadas por Meta distintas para servicio y marketing, más consentimiento. Correo: sin dominio propio verificado, los servicios de envío solo permiten enviar al dueño de la cuenta.

**Reseñas.** Invitar a reseñar en Google al terminar el pago; recompensa validada manualmente por el admin (Google no permite comprobar quién reseñó).

**PWA.** Manifiesto, íconos, service worker, página sin conexión, instalación y experiencia de app en el celular.

**Experiencia visual.** Identidad de marca coherente, animaciones ligeras (CSS 3D sin librerías pesadas salvo modelo 3D real), respetar «reducir movimiento».

**Tareas programadas (cron).** Servicio aparte que llama cada ~2–5 min a un endpoint protegido con `Authorization: Bearer $CRON_SECRET` para liberar reservas vencidas, enviar avisos, otorgar estrellas de cumpleaños y push. Debe ser seguro, idempotente y tolerante a fallos; su falla es crítica porque detiene recordatorios.

**Robustez.** Valores por defecto si la configuración de BD está vacía (evitar caída del sitio); mensajes de error legibles mapeados desde códigos; páginas `/privacidad` y `/terminos` (necesarias para OAuth de Google y para la Ley 29733 de Perú; el texto debe reflejar datos reales del cliente y ser revisado por él).

## Lecciones y errores conocidos
- Redirecciones a `0.0.0.0:3000` por usar `request.url` → usar `SITE_URL`.
- Imports que pasan el chequeo de tipos pero fallan en el empaquetador (`import * as lib` vs `import lib from`) → siempre build real.
- Pruebas que cuentan datos de otros usuarios → acotar siempre por usuario.
- Archivo local desactualizado pisa una corrección al empaquetar → sincronizar antes del ZIP.
- La traducción automática de Chrome rompe paneles (EasyPanel, Supabase; «¡Algo salió mal!») → desactivarla o recargar; la acción suele haberse guardado.
- Sin dominio propio no se puede enviar correo a clientes ni completar ciertas validaciones.
- Recompensas sin idempotencia por cita/periodo generan duplicados.
- Un rol que no puede ver el registro que debe confirmar devuelve NOT_FOUND → revisar políticas de lectura de cada rol.
- Funciones de fecha cerca de medianoche y reglas de «mínimo de anticipación» rompen flujos de atención inmediata → definir reglas específicas por modo.
- Pruebas que insertan como rol autenticado fallan por permisos → preparar datos con rol de servicio.
- Verificar siempre el resultado en el sitio real tras desplegar; si el sandbox no sale a internet, verificar desde el navegador.

## Lista de verificación final
- [ ] Build real y pruebas automáticas en verde.
- [ ] `.env.example` completo, sin valores; `SITE_URL` usada en todas las redirecciones.
- [ ] Migraciones en orden documentado; seed sin datos reales sensibles.
- [ ] Cron desplegado y autenticado (sin 401).
- [ ] Manuales por rol y documento de alcance entregados.
- [ ] Lista de credenciales/datos pendientes del cliente.
- [ ] Prueba en sitio real: registro, login, flujo principal, pagos, notificación.