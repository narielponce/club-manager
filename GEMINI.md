# GEMINI.md - Club Manager

This project is a comprehensive club management system featuring a FastAPI backend, a Vue 3 frontend, and a static landing page. It supports multi-tenancy (multiple clubs) and role-based access control.

## Project Overview

- **Backend**: FastAPI (Python 3.10+), SQLAlchemy (ORM), Alembic (Migrations), Pydantic (Schemas).
- **Frontend**: Vue 3 (Vite), Bootstrap 5, Chart.js (Reporting), Vue Router.
- **Database**: PostgreSQL (managed via `psycopg2-binary`).
- **Infrastructure**: Docker Compose, Nginx (Proxy).

## Core Architecture

### Backend (`/backend`)
- **Entry Point**: `backend/main.py` (FastAPI app, lifespan events, middleware).
- **Models**: `backend/models.py` (SQLAlchemy models).
- **Schemas**: `backend/schemas.py` (Pydantic models for API request/response).
- **Routers**: `backend/routers/` (Modular API routes).
- **Security**: `backend/security.py` (JWT authentication, password hashing).
- **Migrations**: `backend/alembic/versions/` (Database schema history).
- **Static Files**: Serves uploads (e.g., club logos) from `/code/uploads`.

### Frontend (`/frontend`)
- **Entry Point**: `frontend/src/main.js` (Vue app initialization).
- **Layouts**: `frontend/src/layouts/` (Default and Login layouts).
- **Views**: `frontend/src/views/` (SPA pages).
- **Components**: `frontend/src/components/` (Reusable Vue components).
- **Services**: `frontend/src/services/` (API client, Auth, Session management).
- **Landing Page**: `frontend/landing/` (Static HTML/CSS/JS site).

## Core Models & Relationships
- **Club**: The top-level entity for multi-tenancy.
- **User**: System users with roles (`admin`, `tesorero`, `comision`, `profesor`, `socio`, `superadmin`).
- **Member**: Club members, linked to activities.
- **Activity**: Offered by clubs, can have a professor (User).
- **Debt & Payment**: Financial tracking for member fees and activities.
- **Transaction**: Records of income and expenses.

## Development Standards & Mandates

### Backend Development
1. **Migrations**: NEVER modify `models.py` without creating a corresponding Alembic migration (`alembic revision --autogenerate`).
2. **Type Safety**: Always use Pydantic schemas in `schemas.py` for API data validation.
3. **Locale**: The backend is configured for `es_ES.UTF-8` to ensure Spanish month names in reports.
4. **API Patterns**: Follow the RESTful conventions established in the `routers/` directory. Use the `/api` root path.
5. **Authentication**: Most routes require authentication and specific role checks.

### Frontend Development
1. **Styling**: Prefer Bootstrap 5 classes for consistent UI.
2. **Components**: Use the Options API or Composition API (be consistent with surrounding files).
3. **State Management**: Current implementation uses specialized services in `src/services/` and local component state.
4. **Assets**: Logos and other dynamic images are fetched from the backend's `/uploads` path.

### General
- **Docker**: The project is designed to run in containers. Use `docker-compose.yml` for development and production.
- **Environment**: Sensitive configurations (DB URLs, superadmin credentials, API keys) are managed via `.env` files.
- **Nginx**: Handles reverse proxying and serves the landing page separately from the Vue SPA.

## Common Tasks
- **Add a Migration**: `docker-compose exec backend alembic revision --autogenerate -m "description"` followed by `docker-compose exec backend alembic upgrade head`.
- **Install Backend Package**: Add to `backend/requirements.txt` and rebuild.
- **Install Frontend Package**: `npm install` in `frontend/` and update `package.json`.
