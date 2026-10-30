#!/usr/bin/env bash
set -e

# Configuración por defecto de rama
BRANCH="${1:-stable-working-version}"

echo "=================================================="
echo "🚀 Iniciando despliegue de Club Manager"
echo "📅 Fecha: $(date)"
echo "🌿 Rama: $BRANCH"
echo "=================================================="

# 1. Actualizar repositorio
echo "📥 1. Actualizando código desde Git..."
git fetch origin "$BRANCH"
git checkout "$BRANCH"
git reset --hard "origin/$BRANCH"

# 2. Detectar comando Docker Compose
if docker compose version >/dev/null 2>&1; then
    DC="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
    DC="docker-compose"
else
    echo "❌ Error: Ni 'docker compose' ni 'docker-compose' están instalados."
    exit 1
fi
echo "🐳 Usando: $DC"

# 3. Reconstruir y levantar contenedores
echo "🔨 2. Reconstruyendo imágenes y levantando servicios..."
$DC up -d --build

# 4. Aplicar migraciones
echo "🔄 3. Aplicando migraciones de base de datos..."
sleep 3
$DC exec -T backend alembic -c backend/alembic.ini upgrade head

# 5. Recarga de Nginx para aplicar certificados actualizados
echo "🔒 4. Recargando Nginx para aplicar certificados..."
$DC exec -T proxy nginx -s reload || true

# 6. Limpieza de imágenes huérfanas
echo "🧹 5. Limpiando imágenes y capas Docker antiguas..."
docker image prune -f

echo "=================================================="
echo "✅ ¡Despliegue finalizado exitosamente!"
echo "📊 Estado de los contenedores:"
$DC ps
echo "=================================================="
