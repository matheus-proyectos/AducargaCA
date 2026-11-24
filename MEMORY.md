# Memory Index for ADUCARGA PWA Conversion

- [PWA icons generated](src/app/api/health/route.ts) — logo192.png (1349 bytes), logo512.png (5330 bytes), apple-touch-icon.png (1293 bytes)
- [Offline page created](src/app/offline/page.tsx) — shows "Sin conexión" UI
- [Service worker registration](src/components/ServiceWorkerRegister.tsx) — registers /sw.js in production
- [Manifest link added](src/app/layout.tsx) — <link rel="manifest" href="/manifest.json">
- [Theme-color set](src/app/layout.tsx) — <meta name="theme-color" content="#0C2C52">
- [AppleWebApp config](src/app/layout.tsx) — appleWebApp: { capable: true, statusBarStyle: "default", title: "ADUCARGA" }
- [output: "standalone"](next.config.mjs) — for Docker/EasyPanel deployment
- [NEXT_PUBLIC_SITE_URL](.env.example) — critical for reverse proxy redirects
- [CRON_SECRET](.env.example) — for protected cron endpoint
- [Health endpoint](src/app/api/health/route.ts) — public, no auth, for Docker HEALTHCHECK
- [Cron endpoint](src/app/api/cron/dispatch/route.ts) — Bearer token auth, idempotent retry logic
- [Build passes](npm run build) — ✓ compiled successfully
- [Typecheck passes](npm run typecheck) — ✓ no errors