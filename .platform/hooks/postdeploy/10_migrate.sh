#!/usr/bin/env bash
set -euo pipefail

echo "[postdeploy] waiting for app container to be up..."

# EB tags the running image as aws_beanstalk/current-app. Use that to find the container.
# Retry for ~60s in case docker is still pulling/starting.
for i in $(seq 1 30); do
  CID=$(docker ps --filter "ancestor=aws_beanstalk/current-app" --format "{{.ID}}" | head -n1 || true)
  if [ -n "${CID:-}" ]; then
    break
  fi
  sleep 2
done

if [ -z "${CID:-}" ]; then
  echo "[postdeploy] ERROR: app container not found"
  exit 1
fi

echo "[postdeploy] running migrations in container $CID..."
docker exec -i "$CID" python manage.py migrate --noinput

echo "[postdeploy] migrations done."