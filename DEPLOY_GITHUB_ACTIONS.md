# Deploy to GitHub Actions (Scheduled)

## Overview
Runs the scraper on a schedule (every 30 min by default) using GitHub Actions. **Completely free**, no server cost, persistent SQLite storage via git commits.

## Setup

### 1. Add secrets to your GitHub fork
GitHub Actions use "secrets" to securely store credentials without exposing them in logs.

- Go to your fork: `https://github.com/yourusername/streeteasy-monitor`
- Settings → Secrets and variables → Actions
- Click "New repository secret" for each:
  - **SMTP_SERVER**: `smtp.gmail.com` (or your provider)
  - **SMTP_PORT**: `587`
  - **SMTP_USERNAME**: `your-email@gmail.com`
  - **SMTP_PASSWORD**: `your-app-password` (Gmail: use [app password](https://support.google.com/accounts/answer/185833))
  - **EMAIL_RECIPIENT**: `your-email@gmail.com`

### 2. Commit and push the workflow
```bash
git add .github/workflows/scrape.yml
git commit -m "Add GitHub Actions scheduled scraper"
git push origin main
```

### 3. Verify it's running
- Go to your fork → "Actions" tab
- You should see "StreetEasy Monitor - Scheduled Scraper"
- Click it to see runs, logs, and status

## How It Works
1. Workflow triggers on schedule (every 30 min, or manually via Actions tab)
2. GitHub spins up a Linux runner, installs Python + deps
3. Runs `python main.py` with your SMTP secrets as env vars
4. After each run, commits any DB updates (`data/db.sqlite3`) back to your repo
5. Next run pulls the latest DB with all previous listings

## Schedule (Cron Syntax)
Edit `.github/workflows/scrape.yml` line 6:
```yaml
- cron: '*/30 * * * *'  # Every 30 minutes
- cron: '0 */2 * * *'   # Every 2 hours
- cron: '0 9,17 * * *'  # 9 AM and 5 PM UTC daily
```
[Cron expression reference](https://crontab.guru/)

## Persistent Storage
- SQLite DB (`data/db.sqlite3`) is committed to your fork after each run
- Each run pulls the latest DB, scrapes new listings, updates the DB, commits changes
- Full history preserved in git (can revert if needed)

## Logs & Debugging
- Actions tab → click latest run → see full logs
- Check for SMTP errors, network issues, etc.
- Logs are retained for 90 days by default

## Manual Trigger
- Actions tab → "StreetEasy Monitor - Scheduled Scraper" → "Run workflow" → "Run workflow"
- Useful for testing or immediate runs without waiting for schedule

## Limitations
- GitHub Actions free tier: 2000 minutes/month (plenty for 30-min schedule)
- Each run takes ~30-60 seconds
- Network requests (StreetEasy scraping) must succeed within timeout (6 hours)

## Cost
**Free** — GitHub Actions free tier includes 2000 minutes/month for public/private repos.

## Troubleshooting
- **Workflow not showing**: Push `.github/workflows/scrape.yml` to your fork (not upstream)
- **Secrets not working**: Redeploy workflow after adding secrets, or trigger manually
- **"No new listings" but expect some**: StreetEasy may not have listings matching your filters, or they're already in the DB
- **Git commit fails**: Check your fork's settings allow Actions to write (usually enabled by default)
