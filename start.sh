#!/bin/sh
# config.py resolves paths relative to /app/../ = /
# UPLOAD_DIR = /uploads, DB_PATH = /data/eihei.db
# Redirect both to the persistent volume at /mnt/data

mkdir -p /mnt/data/uploads /mnt/data/db

# Create symlinks only if they don't already exist
[ -e /uploads ] || ln -sf /mnt/data/uploads /uploads
[ -e /data ]    || ln -sf /mnt/data/db /data

exec /usr/bin/supervisord -c /etc/supervisor/conf.d/app.conf
