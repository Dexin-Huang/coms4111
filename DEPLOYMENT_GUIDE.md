# Google Cloud Platform Deployment Guide

## Quick Deployment Steps

### 1. SSH into Your GCP VM

```bash
# From your local machine
gcloud compute ssh <your-vm-name> --zone=<your-zone>

# OR if you have the external IP
ssh <your-username>@<external-ip>
```

### 2. Clone the Repository

```bash
cd ~
git clone https://github.com/Dexin-Huang/coms4111.git
cd coms4111/Part3/webserver
```

### 3. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install flask sqlalchemy psycopg2-binary click
```

### 4. Run the Application

**Option A: Foreground (for testing)**
```bash
python server.py
```

**Option B: Background with nohup**
```bash
nohup python server.py > flask.log 2>&1 &
```

**Option C: Using screen (recommended)**
```bash
# Start screen session
screen -S flask

# Run the app
python server.py

# Detach: Press Ctrl+A, then D
# Reattach later: screen -r flask
```

### 5. Access the Application

```
http://<your-vm-external-ip>:8111
```

---

## Option 2: Auto-Deployment with Git Pull

### Set Up Auto-Update Script

Create `~/update-app.sh`:

```bash
#!/bin/bash
cd ~/coms4111/Part3/webserver

# Pull latest changes
git pull origin main

# Restart the application
pkill -f "python server.py"
sleep 2
source venv/bin/activate
nohup python server.py > flask.log 2>&1 &

echo "Application updated and restarted!"
```

Make it executable:
```bash
chmod +x ~/update-app.sh
```

### Usage:
```bash
# Whenever you push to GitHub, run this on GCP:
ssh <your-vm> "~/update-app.sh"
```

---

## Option 3: Automatic Deployment with Cron

### Set up periodic auto-pull (every 5 minutes):

```bash
# Edit crontab
crontab -e

# Add this line:
*/5 * * * * cd ~/coms4111/Part3/webserver && git pull origin main > /dev/null 2>&1
```

**Note:** This only pulls code. You still need to restart Flask manually.

---

## Option 4: GitHub Webhooks (Advanced)

### 1. Install webhook listener on GCP:

```bash
pip install Flask-Webhooks
```

### 2. Create webhook listener (webhook_listener.py):

```python
from flask import Flask, request
import subprocess

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        # Run update script
        subprocess.run(['/home/<username>/update-app.sh'])
        return 'Updated', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)
```

### 3. Configure GitHub webhook:
- Go to: https://github.com/Dexin-Huang/coms4111/settings/hooks
- Add webhook: `http://<your-vm-ip>:9000/webhook`
- Content type: `application/json`
- Events: Push events

---

## Firewall Configuration

Make sure port 8111 is open:

```bash
gcloud compute firewall-rules create allow-flask \
    --allow tcp:8111 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow Flask app on port 8111"
```

Check existing rules:
```bash
gcloud compute firewall-rules list
```

---

## Production Setup (Systemd Service)

### 1. Create service file: `/etc/systemd/system/flask-app.service`

```ini
[Unit]
Description=Flask Medical Records Application
After=network.target

[Service]
Type=simple
User=<your-username>
WorkingDirectory=/home/<your-username>/coms4111/Part3/webserver
Environment="PATH=/home/<your-username>/coms4111/Part3/webserver/venv/bin"
ExecStart=/home/<your-username>/coms4111/Part3/webserver/venv/bin/python server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### 2. Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable flask-app
sudo systemctl start flask-app

# Check status
sudo systemctl status flask-app

# View logs
sudo journalctl -u flask-app -f
```

### 3. Control commands:

```bash
sudo systemctl stop flask-app      # Stop
sudo systemctl restart flask-app   # Restart
sudo systemctl status flask-app    # Check status
```

---

## Troubleshooting

### Check if Flask is running:
```bash
ps aux | grep python
```

### Check logs:
```bash
cat flask.log
tail -f flask.log  # Follow logs in real-time
```

### Kill Flask process:
```bash
pkill -f "python server.py"
```

### Test database connection:
```bash
python -c "from sqlalchemy import create_engine; engine = create_engine('postgresql://wl2822:234471@34.139.8.30/proj1part2'); conn = engine.connect(); print('Connected!'); conn.close()"
```

### Check open ports:
```bash
sudo netstat -tulpn | grep 8111
```

---

## Quick Reference Commands

```bash
# Deploy from scratch
git clone https://github.com/Dexin-Huang/coms4111.git
cd coms4111/Part3/webserver
python3 -m venv venv
source venv/bin/activate
pip install flask sqlalchemy psycopg2-binary click
screen -S flask
python server.py

# Update existing deployment
cd ~/coms4111/Part3/webserver
git pull
pkill -f "python server.py"
source venv/bin/activate
nohup python server.py > flask.log 2>&1 &

# Check status
ps aux | grep python
tail flask.log
```

---

## What You Need

1. **GCP VM Details:**
   - VM name: `<your-vm-name>`
   - Zone: `<your-zone>`
   - External IP: `<your-external-ip>`

2. **GitHub Repository:**
   - URL: https://github.com/Dexin-Huang/coms4111.git
   - Branch: `main`

3. **Database:**
   - Already configured in server.py
   - Host: 34.139.8.30
   - Database: proj1part2
   - Username: wl2822
   - Password: 234471

---

## Recommended Approach

**For this project, I recommend:**

1. **Use screen + manual git pull** (simplest)
2. **Set up systemd service** (for auto-restart)
3. **Use update script** (for easy updates)

This gives you:
- Easy deployment
- Automatic restart on crash
- Quick updates when you push to GitHub
- Good enough for course project

**Skip webhooks** - they're overkill for a course project and add complexity.
