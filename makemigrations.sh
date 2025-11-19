#!/bin/sh
set -e

# Verifica que se haya pasado un mensaje para la migración
if [ -z "$1" ]; then
  echo "Error: Por favor, proporciona un mensaje para la migración."
  echo "Uso: ./makemigrations.sh \"Tu mensaje de migración\""
  exit 1
fi

echo "Generando script de migración..."
docker compose exec backend alembic -c backend/alembic.ini revision --autogenerate -m "$1"
echo "Script generado con éxito."

