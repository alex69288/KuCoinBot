#!/bin/bash
set -e
# Рабочая директория внутри контейнера
cd /app || true

# Если мы на корне проекта и есть папка backend, перейдём в неё
if [ -d backend ]; then
  cd backend || true
fi

if [ ! -f dist/index.js ]; then
  echo "dist not found, running npm install and npm run build"
  npm install --ignore-scripts --no-optional --legacy-peer-deps
  npm run build
fi

# Заменяем текущий процесс на node (чтобы корректно обрабатывать сигналы)
exec node dist/index.js
