# Deployment Guide for StreetEasy Monitor Web Interface

This guide covers deploying the Flask web interface to a server for remote access.

## Prerequisites

- A server or cloud platform (Render, Heroku, Railway, DigitalOcean, etc.)
- Your `.env` configuration ready
- Git repository access

## Security Checklist Before Deployment

**CRITICAL: Complete these steps before deploying publicly:**

1. **Generate a secure SECRET_KEY**
   ```bash
   python -c "import os; print(os.urandom(24).hex())"
   ```
   Add to your `.env` file:
   ```
   SECRET_KEY=<generated-key-here>
   ```

2. **Set a strong admin password** (REQUIRED - app will not start without this)
   ```
   ADMIN_PASSWORD=<your-unique-strong-password>
   ```

   **Note:** Never use example passwords from documentation. Create your own unique password.

3. **Configure SMTP for email notifications**
   - Use app-specific passwords for Gmail
   - Never use your main email password

4. **Verify `.env` is in `.gitignore`**
   ```bash
   cat .gitignore | grep .env
   ```

## Deployment Options

### Option 1: Render (Recommended - Free Tier Available)

1. **Create a new Web Service on Render**
   - Connect your GitHub repository
   - Select "Python" as the environment

2. **Configure Build Settings**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn -w 4 -b 0.0.0.0:$PORT "app:create_app()"`

3. **Add Environment Variables** in Render Dashboard
   ```
   SECRET_KEY=<your-secret-key>
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=<your-password>
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=<your-email>
   SMTP_PASSWORD=<your-smtp-password>
   EMAIL_RECIPIENT=<recipient-email>
   MAPS_STATIC_API_KEY=<your-api-key>
   ```

4. **Add gunicorn to requirements.txt** (if not present)
   ```bash
   echo "gunicorn==21.2.0" >> requirements.txt
   ```

5. **Deploy!**

### Option 2: Heroku

1. **Install Heroku CLI and login**
   ```bash
   heroku login
   ```

2. **Create new app**
   ```bash
   heroku create your-app-name
   ```

3. **Set environment variables**
   ```bash
   heroku config:set SECRET_KEY=<your-secret-key>
   heroku config:set ADMIN_USERNAME=admin
   heroku config:set ADMIN_PASSWORD=<your-password>
   # ... add all other env vars
   ```

4. **Create Procfile** in root directory
   ```
   web: gunicorn -w 4 -b 0.0.0.0:$PORT "app:create_app()"
   ```

5. **Deploy**
   ```bash
   git push heroku main
   ```

### Option 3: DigitalOcean App Platform

1. **Create a new app** from your GitHub repo
2. **Set environment variables** in the dashboard
3. **Configure run command**: `gunicorn -w 4 -b 0.0.0.0:$PORT "app:create_app()"`
4. **Deploy**

### Option 4: Self-Hosted (VPS/Cloud Server)

1. **SSH into your server**
   ```bash
   ssh user@your-server-ip
   ```

2. **Clone repository**
   ```bash
   git clone https://github.com/yourusername/streeteasy-monitor.git
   cd streeteasy-monitor
   ```

3. **Set up Python environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Create `.env` file** with your configuration

5. **Install and configure Nginx**
   ```bash
   sudo apt install nginx
   ```

   Create `/etc/nginx/sites-available/streeteasy-monitor`:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://127.0.0.1:8002;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

   Enable site:
   ```bash
   sudo ln -s /etc/nginx/sites-available/streeteasy-monitor /etc/nginx/sites-enabled/
   sudo systemctl restart nginx
   ```

6. **Set up systemd service**
   Create `/etc/systemd/system/streeteasy-monitor.service`:
   ```ini
   [Unit]
   Description=StreetEasy Monitor Flask App
   After=network.target

   [Service]
   User=your-user
   WorkingDirectory=/path/to/streeteasy-monitor
   Environment="PATH=/path/to/streeteasy-monitor/.venv/bin"
   ExecStart=/path/to/streeteasy-monitor/.venv/bin/gunicorn -w 4 -b 127.0.0.1:8002 "app:create_app()"
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

   Enable and start:
   ```bash
   sudo systemctl enable streeteasy-monitor
   sudo systemctl start streeteasy-monitor
   ```

7. **Set up SSL with Let's Encrypt** (Recommended)
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

## Post-Deployment

1. **Test the login**
   - Visit your deployed URL
   - Login with your admin credentials
   - Verify dashboard loads

2. **Test a search**
   - Navigate to "Run Search"
   - Submit a search with valid parameters
   - Check if results appear

3. **Monitor logs**
   - Check application logs for errors
   - Monitor email notifications

4. **Set up monitoring** (optional)
   - Use UptimeRobot or similar to monitor uptime
   - Set up error alerting

## GitHub Actions Integration

The existing GitHub Actions workflow will continue to run on schedule independently from the web interface. Both can coexist:
- **GitHub Actions**: Automated monitoring every 2 hours
- **Web Interface**: Manual searches and viewing results on demand

## Rate Limiting

The application includes built-in rate limiting:
- Login: 10 attempts per minute
- Search: 5 per minute
- All routes: 200 per day, 50 per hour

Adjust in [app/__init__.py](app/__init__.py) if needed.

## Troubleshooting

### "ADMIN_PASSWORD environment variable must be set"
- The app requires ADMIN_PASSWORD to be set explicitly
- Add it to your environment variables in your hosting platform
- Never use default or example passwords

### "Internal Server Error" on login
- Check SECRET_KEY is set in environment variables
- Verify ADMIN_PASSWORD is set correctly

### Email notifications not sending
- Verify SMTP credentials are correct
- Check SMTP_PORT (587 for TLS, 465 for SSL)
- For Gmail, ensure you're using an App Password

### Database not persisting
- Ensure `data/` directory exists and is writable
- Check database file permissions

### Rate limit errors
- Adjust rate limits in app initialization
- Consider using Redis for distributed rate limiting

## Security Best Practices

1. **Always use HTTPS** in production (use Let's Encrypt for free SSL)
2. **Keep dependencies updated**: `pip install --upgrade -r requirements.txt`
3. **Enable firewall** on your server
4. **Regular backups** of the SQLite database
5. **Monitor access logs** for suspicious activity
6. **Use strong passwords** for admin account
7. **Consider adding 2FA** for additional security

## Support

For issues or questions, please open an issue on GitHub.
