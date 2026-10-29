# Contexto del Proyecto: Club Manager & Raíz Digital

Este documento resume la arquitectura, funcionalidad y estrategia de despliegue del ecosistema **Club Manager** (SaaS) y la página institucional de **Raíz Digital**.

## 1. Funcionalidad del Desarrollo (Arquitectura de Software)

El sistema es una plataforma multi-inquilino diseñada para la administración integral de clubes, asociaciones y centros vecinales. Se divide en tres bloques principales:

### A. Backend (FastAPI / Python)
- **API RESTful de Alta Velocidad**: Construida con FastAPI (Python 3.12) y Pydantic para la validación estricta de esquemas de datos.
- **Base de Datos y ORM**: Utiliza PostgreSQL como motor relacional, SQLAlchemy como ORM para la interacción orientada a objetos y Alembic para el control de versiones (migraciones) del esquema de la base de datos.
- **Seguridad Multi-nivel**: Sistema de autenticación basado en JWT con control de acceso por roles granulados (`admin`, `tesorero`, `comision`, `profesor`, `socio`, `superadmin`).
- **Estructura Multi-tenant**: Toda la lógica de negocio (socios, deudas, pagos, transacciones, actividades) aísla la información conectándola a una entidad raíz (el Club).
- **Soporte Regional**: El contenedor está explícitamente configurado con el *locale* `es_ES.UTF-8` para manejar correctamente conversiones de moneda y fechas en los reportes financieros en español.

### B. Frontend SaaS (Vue 3 / JavaScript)
- **Single Page Application (SPA)**: Desarrollada con Vue 3 y construida (built) usando Vite para máxima velocidad y optimización en producción.
- **UI y Experiencia de Usuario**: Utiliza Bootstrap 5 para el diseño de componentes y Chart.js para tableros de mando y gráficos de reportes.
- **Servicios Integrados**: Se comunica exclusivamente con el backend a través del endpoint `/api/` manejando los tokens de sesión de manera local.

### C. Landing Page Institucional (HTML / CSS Moderno)
- **Web de Presentación Estática**: Sirve como el escaparate digital de la agencia tecnológica Raíz Digital.
- **Estética "Premium"**: Modernizada recientemente (abandonando jQuery y Bootstrap 4), ahora funciona con Bootstrap 5, tipografía *Inter*, y un diseño *Glassmorphism* moderno, con todas las etiquetas preparadas para un óptimo posicionamiento SEO.

---

## 2. Infraestructura y Despliegue (Docker)

Todo el ciclo de vida de la aplicación, tanto en desarrollo como en el Droplet (producción), está automatizado mediante **Docker Compose**.

### Estructura de Contenedores
El archivo maestro `docker-compose.yml` orquesta cinco servicios críticos:

1. **`proxy` (Nginx)**: Actúa como el *Reverse Proxy* perimetral del sistema.
   - Fuerza todo el tráfico HTTP no validado a HTTPS (SSL).
   - Redirige las peticiones al dominio `raizdigital.com.ar` hacia los archivos estáticos de la Landing Page.
   - Gestiona el tráfico de `sociosass.raizdigital.com.ar`, enrutando de forma limpia las sub-rutas:
     - `/api/` -> Envía al contenedor Backend.
     - `/uploads/` -> Sirve estáticos persistentes (logos, comprobantes).
     - `/` -> Sirve la aplicación Vue (Frontend).
2. **`backend`**: Ejecuta el servidor web *Uvicorn* con la aplicación FastAPI.
3. **`frontend`**: En producción, la aplicación Vue se compila y encapsula en una imagen liviana de Nginx interno para distribuir los *assets*.
4. **`db`**: Contenedor de PostgreSQL 15 blindado mediante volúmenes para la persistencia de datos seguros.
5. **`certbot`**: Contenedor programado para validar y emitir los certificados SSL de *Let's Encrypt*, permitiendo que Nginx encripte todas las conexiones hacia el mundo exterior.

### Flujo Operativo en Producción
- **Sincronización en Caliente (Hot-Sync)**: Las carpetas que requieren ser servidas instantáneamente (como la Landing Page y los *uploads*) se montan como volúmenes de host directo. Esto permite que una simple sincronización con el repositorio (`git pull`) aplique cambios estéticos a la landing en tiempo real, sin requerir la compilación de ninguna nueva imagen de Docker.
- **Renovación SSL Integrada**: El contenedor `certbot` dispone de un *entrypoint* o bucle de ejecución que verifica regularmente la caducidad de los certificados SSL por el método de reto de archivo (*webroot*), garantizando que el sitio mantenga su status de confianza ininterrumpidamente.
- **Automatización CI/CD (GitHub Actions)**: Todo el despliegue está automatizado mediante `.github/workflows/deploy.yml`. Al realizar `push` a las ramas principales (`main` o `stable-working-version`), GitHub Actions ejecuta las validaciones de compilación y se conecta vía SSH a la VPS para actualizar el código, reconstruir los contenedores afectados con Docker Compose y ejecutar las migraciones de Alembic sin intervención manual.
