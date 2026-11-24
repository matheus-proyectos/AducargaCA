---
name: desplegar-nextjs-easypanel
description: Despliega una app Next.js + Supabase en un VPS con EasyPanel (Docker, Traefik) y la migra a otro VPS o dominio propio. Incluye todos los fallos conocidos y su solución.
---

# Desplegar Next.js + Supabase en EasyPanel (VPS) — procedimiento probado

Origen: despliegue real de "Barbería The Mesías" (Next.js 16 standalone, Supabase, Google OAuth, cron) en un VPS Hostinger con EasyPanel 2.37. Tono con el usuario: formal, estructurado, en español. **Antes de tocar EasyPanel, decir al usuario qué se va a hacer.** El usuario pega personalmente secretos y tokens; nunca intentes extraerlos de la pantalla.

## 0. Requisitos y datos que pedir al cliente
- Cuenta GitHub (repo privado), cuenta Supabase del cliente, VPS con EasyPanel, dominio (opcional al inicio: EasyPanel da uno gratis `*.easypanel.host`).
- Cuenta Google (Cloud) del cliente para OAuth, número de WhatsApp Business y dominio (para Resend) — solo si se activan esos canales.

## 1. Repositorio GitHub (privado)
1. Crear repo privado. Subir el proyecto (ZIP + workflow de extracción, o `git push`).
2. EasyPanel clona por SSH: en EasyPanel → app → Fuente → Git, copiar la **deploy key** pública y añadirla en GitHub → Settings → Deploy keys (solo lectura).
3. EasyPanel 2.37 **no tiene webhook de auto-deploy fiable ni cron**: cada cambio se despliega con el botón **Implementar**.

## 2. Supabase (cuenta del cliente)
1. Crear proyecto. Ejecutar en SQL Editor las migraciones en orden (`supabase/migrations/*.sql`) y luego `seed.sql`.
2. Anotar: URL del proyecto, `anon` key, `service_role` key (usar las claves *legacy*). Solo el usuario las pega.
3. Authentication → URL Configuration: **Site URL** = URL pública final; **Redirect URLs** = `https://<dominio>/**`.
4. Trigger SQL en editor: `window.monaco.editor.getEditors()[0].setValue(sql)` y luego Ctrl+Enter.
5. Plan gratuito pausa proyectos inactivos: el cron cada 2 min lo mantiene activo; para producción real, plan de pago.

## 3. App en EasyPanel
1. Proyecto → + Servicio → App. Fuente: Git (SSH) rama `main`. Build: **Dockerfile**.
2. **Build args / variables** (las `NEXT_PUBLIC_*` se incrustan al compilar, por eso van como *build args* y exigen reimplementar al cambiar):
   - `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, `NEXT_PUBLIC_SITE_URL` (URL pública, sin `/` final).
   - Solo servidor: `SUPABASE_SERVICE_ROLE_KEY`, `CRON_SECRET` (largo y aleatorio), y opcionales `WHATSAPP_*`, `RESEND_API_KEY`, `EMAIL_FROM`, `MERCADOPAGO_*`.
3. Dominios: puerto del contenedor **3000**, HTTPS activado.
4. Implementar. Una compilación tarda ~1–3 min.

## 4. Fallo conocido #1 — redirecciones a `0.0.0.0:3000`
Detrás de Traefik, `request.url` y `request.nextUrl.origin` valen `0.0.0.0:3000`. **Nunca** construir redirecciones con ellos. Usar siempre `SITE_URL` (de `NEXT_PUBLIC_SITE_URL`):
- `auth/callback/route.ts`: `const origin = SITE_URL`.
- `auth/signout/route.ts`: `NextResponse.redirect(new URL("/", SITE_URL), { status: 303 })`.
- `proxy.ts` (middleware): `new URL("/login", SITE_URL)`.
Síntoma típico: el enlace del correo de confirmación o "Cerrar sesión" lleva a `0.0.0.0:3000` (ERR_ADDRESS_INVALID).

## 5. Cron (EasyPanel no trae scheduler)
Crear una segunda app `…-cron`, imagen `busybox:1.36`, variable `CRON_SECRET` (el mismo valor), Avanzado → Comando:
```
sh -c 'while true; do wget -qO- --header="Authorization: Bearer $CRON_SECRET" http://<proyecto>_<servicio-app>:3000/api/cron/dispatch; echo; sleep 120; done'
```
Usa el hostname interno `<proyecto>_<servicio>` (red interna del VPS, no consume internet). Verificar en logs que responde JSON (no 401).

## 6. Google OAuth
1. Google Cloud (cuenta del cliente): proyecto → Auth Platform → pantalla de consentimiento **Externa**, publicar **"En producción"** (scopes básicos: no requiere verificación).
2. Dominios autorizados: dominio de la app y `<ref>.supabase.co`. Páginas legales públicas (`/privacidad`, `/terminos`) y correo de contacto.
3. No subir logo (obligaría a verificación) hasta tener dominio propio.
4. Credenciales OAuth Web: origen JS = dominio app; redirect URI = `https://<ref>.supabase.co/auth/v1/callback`.
5. Supabase → Auth → Providers → Google: activar y pegar Client ID/Secret (el usuario los pega).
6. Si Google muestra "provider is not enabled": falta activar el proveedor.
7. Varias cuentas Google en el navegador: usar `?authuser=<correo>` en la URL de consola para forzar la cuenta correcta. Cuentas corporativas pueden exigir 2SV y bloquear.

## 7. Primer administrador
Registrar al usuario en la app y promoverlo con SQL: `update profiles set role = 'admin' where email = '<correo>';`

## 8. Fallos conocidos de herramientas
- **"¡Algo salió mal!" en EasyPanel**: lo causa la traducción automática de Chrome. Recargar; la acción casi siempre sí se guardó. Mejor desactivar la traducción en esa pestaña.
- IDs de pestaña obsoletos: ejecutar de nuevo `tabs_context_mcp` o crear pestaña.
- Editar en GitHub web: editor CodeMirror → foco en `.cm-content`, `document.execCommand('selectAll')` + `insertText`; las líneas están virtualizadas (scroll en `.cm-scroller`). Verificar con `fetch('/owner/repo/raw/main/<ruta>')` y comparar con booleanos (la herramienta bloquea salidas con URLs/cookies).
- El shell del sandbox no sale a internet salvo lista permitida: las verificaciones HTTP se hacen desde el navegador.

## 9. Lista de pruebas
Registro por correo (enlace → dominio público), Google login, cerrar sesión, reserva (ojo: horarios del seed son Lun–Sáb; en domingo "Atender ahora" da `OUTSIDE_HOURS`), código de referido (referido recibe 50 estrellas de bienvenida; el referidor las recibe cuando la primera visita del referido se completa), cron respondiendo, promoción de admin.

## 10. Migrar a otro VPS / dominio propio del cliente
1. **DNS:** registro A del dominio (y `www`) → IP del nuevo VPS. Esperar propagación.
2. Instalar EasyPanel en el VPS nuevo, recrear proyecto, app (Git SSH: nueva deploy key en GitHub), cron y variables. Mover los secretos (el usuario los pega).
3. EasyPanel → Dominios: añadir el dominio, puerto 3000, HTTPS (Let's Encrypt).
4. Cambiar `NEXT_PUBLIC_SITE_URL` (build arg) al dominio nuevo y **reimplementar**.
5. Supabase → Auth → URL Configuration: nuevo Site URL y Redirect URLs.
6. Google Cloud: orígenes y dominios autorizados al dominio nuevo; ahora sí se puede añadir logo/verificación de marca.
7. Resend: verificar el dominio (SPF/DKIM), actualizar `EMAIL_FROM`. WhatsApp: mantener plantillas.
8. Plan de pago de Supabase antes de producción. Revisar política de privacidad (Ley 29733; no es asesoría legal).
9. Apagar el VPS viejo solo tras comprobar login, reserva, cron y correos en el nuevo.
