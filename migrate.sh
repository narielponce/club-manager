#!/bin/sh
set -e

echo "Aplicando migraciones a la base de datos..."
docker compose exec backend alembic -c backend/alembic.ini upgrade head
echo "Migraciones aplicadas con éxito."
