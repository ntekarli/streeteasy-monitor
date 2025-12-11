# Deploy to Render (Background Worker)

## Prerequisites
1. GitHub account with a fork of `streeteasy-monitor`
2. Render account (free tier available): https://render.com
3. SMTP credentials (Gmail, SendGrid, etc.)

## Quick Deploy Steps

1. **Push code to your fork**
   ```bash
   git add .
   git commit -m "Add Dockerfile and render.yaml for cloud deployment"
   git push origin main
   ```

2. **Create Render account & connect GitHub**
   - Go to https://render.com, sign up with GitHub
   - Grant permission to access your repos

3. **Create a Background Worker service**
   - Dashboard → "New +" → "Background Worker"
   - Name: `streeteasy-monitor`
   - Source: Select your fork (`yourusername/streeteasy-monitor`)
   - Start Command: Leave blank (uses `Dockerfile`)
   - Runtime: Python 3

4. **Add environment variables**
   - Click "Advanced" and add:
     ```
     SMTP_SERVER=smtp.gmail.com
     SMTP_PORT=587
     SMTP_USERNAME=your-email@gmail.com
     SMTP_PASSWORD=your-app-password
     EMAIL_RECIPIENT=your-email@gmail.com
     ```
   - For Gmail, use an [app password](https://support.google.com/accounts/answer/185833)

5. **Deploy**
   - Click "Deploy" → Render builds and starts your worker
   - Monitor logs in Render dashboard

## Auto-Deploy on Future Pushes
Once deployed, every push to `main` in your fork triggers auto-rebuild and restart:
```bash
# Just push code — Render handles the rest
git add .
git commit -m "Update filters"
git push origin main
```

## Persistence & Storage
- **Free tier**: Ephemeral disk (SQLite resets on redeploy)
- **Paid tier** ($7+/mo): Persistent disk keeps `data/db.sqlite3` across deploys
- **Workaround for free**: Store listings in a PostgreSQL DB (Render offers free PostgreSQL tier)

## Scheduled Runs
If you want the scraper to run on a schedule (e.g., every 30 min) instead of continuously:
- Option A: Modify `main.py` to run once then exit, use Render "Cron Jobs"
- Option B: Use GitHub Actions scheduled workflow instead
- Option C: Use a separate cloud scheduler (Cloud Scheduler, EventBridge, etc.)

## Logs & Monitoring
- Render dashboard shows live logs
- Useful commands (once deployed):
  - Monitor errors: Check "Logs" tab in Render
  - Check if running: Look for "Running" status
  - Restart: Click "Restart" in service menu

## Cost
- Free tier: 0.5 GB RAM, monthly usage limit
- Paid tier: $7+/mo for persistent disk + higher limits
- SMTP: Your existing Gmail/SendGrid account (separate cost if applicable)

## Troubleshooting
- **Service crashes**: Check logs for errors (SMTP auth, missing env vars, etc.)
- **SQLite not persisting**: Upgrade to paid tier or switch to PostgreSQL
- **Env vars not loading**: Redeploy after adding vars (sometimes needed)
