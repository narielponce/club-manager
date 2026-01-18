#!/bin/sh
set -e

# Verifica que se haya pasado un mensaje para la migración
if [ -z "$1" ]; then
  echo "Error: Por favor, proporciona un mensaje para la migración."
  echo "Uso: ./makemigrations.sh \"Tu mensaje de migración\""
  exit 1
fi

# Detect user and group IDs, using sudo-provided variables if available
USER_ID=${SUDO_UID:-$(id -u)}
GROUP_ID=${SUDO_GID:-$(id -g)}

echo "Generando script de migración..."
# Execute docker compose with the detected user/group to avoid permission issues
docker compose exec -u "$USER_ID:$GROUP_ID" backend alembic -c backend/alembic.ini revision --autogenerate -m "$1"
echo "Script generado con éxito."

