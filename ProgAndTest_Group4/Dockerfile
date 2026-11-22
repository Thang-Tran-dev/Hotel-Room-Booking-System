# ===== Single-file Dockerfile for the Hotel Booking app (Flask + SQLite) =====
# Place this file next to the "hotel" folder (inside ProgAndTest_GroupXY),
# then build from that folder:
#   docker build -t hotel .
#   docker run -p 5000:5000 -v hotel_data:/data hotel
# Open http://localhost:5000

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000

WORKDIR /app

# Install dependencies first (Docker caches this step, so rebuilds are faster)
COPY hotel/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code
COPY hotel/ .

# Create the start-up script. It stores the database, secret key, e-mail log
# and uploaded images in /data so they are not lost when the container is recreated.
RUN printf '%s\n' \
  '#!/bin/sh' \
  'set -e' \
  'mkdir -p /data/uploads' \
  'ln -sfn /data/hotel.db /app/hotel.db' \
  'ln -sfn /data/secret.key /app/secret.key' \
  'ln -sfn /data/emails.log /app/emails.log' \
  'rm -rf /app/static/uploads' \
  'ln -sfn /data/uploads /app/static/uploads' \
  'exec gunicorn app:A --bind 0.0.0.0:${PORT:-5000} --workers 1 --threads 4' \
  > /entrypoint.sh && chmod +x /entrypoint.sh

EXPOSE 5000
VOLUME /data

# Start the web server (1 worker + 4 threads is safe for SQLite)
ENTRYPOINT ["/entrypoint.sh"]
