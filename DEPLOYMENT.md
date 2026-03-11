# Courier Management System - Deployment Guide

## Production Deployment

### Prerequisites
- Ubuntu 20.04+ or similar Linux distribution
- Python 3.9+
- PostgreSQL 12+
- Redis 6+
- Nginx
- SSL Certificate (Let's Encrypt recommended)

## Step-by-Step Deployment

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-venv postgresql postgresql-contrib redis-server nginx git

# Create application user and directory
sudo useradd -m -u 1000 courier
sudo -u courier mkdir -p /home/courier/app
cd /home/courier/app
```

### 2. Clone Repository

```bash
sudo -u courier git clone <repository-url> .
cd /home/courier/app
```

### 3. Backend Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env with production values
nano .env

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

### 4. Database Setup (PostgreSQL)

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE courier_db;
CREATE USER courier WITH PASSWORD 'strong_password';
ALTER ROLE courier SET client_encoding TO 'utf8';
ALTER ROLE courier SET default_transaction_isolation TO 'read committed';
ALTER ROLE courier SET default_transaction_deferrable TO on;
ALTER ROLE courier SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE courier_db TO courier;
\q
```

### 5. Gunicorn Configuration

Create `/home/courier/app/gunicorn_config.py`:

```python
import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 5
max_requests = 1000
max_requests_jitter = 100
preload_app = True
```

### 6. Systemd Service

Create `/etc/systemd/system/courier.service`:

```ini
[Unit]
Description=Courier Management System
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=courier
WorkingDirectory=/home/courier/app
ExecStart=/home/courier/app/venv/bin/gunicorn \
          --config gunicorn_config.py \
          over_watch.wsgi:application
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable courier
sudo systemctl start courier
```

### 7. Nginx Configuration

Create `/etc/nginx/sites-available/courier`:

```nginx
upstream courier {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name example.com www.example.com;
    client_max_body_size 50M;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name example.com www.example.com;
    client_max_body_size 50M;

    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    # Static files
    location /static/ {
        alias /home/courier/app/staticfiles/;
    }

    # Media files
    location /media/ {
        alias /home/courier/app/media/;
    }

    # API and application
    location / {
        proxy_pass http://courier;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/courier /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

### 8. SSL Certificate (Let's Encrypt)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot certonly --nginx -d example.com -d www.example.com
```

### 9. Frontend Deployment

#### Build React App

```bash
cd /home/courier/app/frontend
npm install
npm run build
```

#### Serve with Nginx

The Nginx configuration serves the React build files from the static directory.

### 10. Backup and Maintenance

#### Database Backup

```bash
# Backup script
#!/bin/bash
BACKUP_DIR="/home/courier/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
sudo -u postgres pg_dump courier_db > $BACKUP_DIR/courier_db_$TIMESTAMP.sql
```

#### Log Rotation

Create `/etc/logrotate.d/courier`:

```
/home/courier/app/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    copytruncate
}
```

### 11. Monitoring and Logging

#### Install Monitoring Tools

```bash
# Option 1: Prometheus + Grafana
# Option 2: New Relic
# Option 3: Datadog
```

#### Check Service Status

```bash
systemctl status courier
journalctl -u courier -f
```

### 12. Scaling Considerations

For large deployments:

1. **Load Balancing**: Use HAProxy or AWS/GCP load balancers
2. **Database Replication**: Set up PostgreSQL replication
3. **Caching**: Use Redis for caching and sessions
4. **CDN**: Use CloudFlare or AWS CloudFront for static files
5. **Async Tasks**: Use Celery with Redis for background jobs
6. **Container Orchestration**: Use Docker + Kubernetes for scaling

### 13. Security Hardening

```bash
# Firewall configuration
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Enable fail2ban
sudo apt install -y fail2ban
sudo systemctl enable fail2ban

# Configure SSH key-based authentication
# Disable password authentication
sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo systemctl restart ssh
```

## Troubleshooting

### Check Logs

```bash
# Application logs
journalctl -u courier -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql.log
```

### Database Issues

```bash
# Check database connection
python manage.py dbshell

# Run migrations again
python manage.py migrate

# Check database size
sudo -u postgres psql -c "SELECT pg_size_pretty(pg_database_size('courier_db'));"
```

### Memory and CPU Usage

```bash
# Monitor system resources
top
htop
ps aux | grep gunicorn
```

## Performance Optimization

1. **Caching**: Enable Redis caching for frequent queries
2. **Database**: Add indexes for frequently searched fields
3. **CDN**: Serve static files through CDN
4. **Compression**: Enable gzip compression in Nginx
5. **SQL Optimization**: Use `select_related()` and `prefetch_related()`

## Updating Application

```bash
cd /home/courier/app
source venv/bin/activate
git pull origin main
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
systemctl restart courier
```

## Health Checks

Add a health check endpoint in Django:

```python
# In urls.py
path('api/health/', views.health_check, name='health_check')

# In views.py
def health_check(request):
    return JsonResponse({'status': 'healthy'})
```

Monitor with:

```bash
curl https://example.com/api/health/
```
