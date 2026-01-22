# Quick Setup Guide

## 1. Install New Dependencies

```bash
pip install -r requirements.txt
```

This adds:
- Flask-Login (authentication)
- Flask-Limiter (rate limiting)

## 2. Configure Environment Variables

Copy the example file and edit with your values:

```bash
cp .env.example .env
```

**Required for Web Interface:**

```bash
# Generate a secure secret key
python3 -c "import os; print(os.urandom(24).hex())"
# Add to .env as SECRET_KEY=<generated-key>

# Set admin credentials (REQUIRED - app won't start without this)
SECRET_KEY=<generated-key-from-above>
ADMIN_USERNAME=admin
ADMIN_PASSWORD=<your-strong-password-here>
```

**Important:** The app will fail to start if `ADMIN_PASSWORD` is not set. This is intentional for security.

**Already configured (if you have them):**
- SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD
- EMAIL_RECIPIENT
- MAPS_STATIC_API_KEY
- Search parameters (MIN_PRICE, MAX_PRICE, etc.)

## 3. Test Locally

```bash
python3 -m app.app
```

Visit: http://localhost:8002

**Login with:**
- Username: `admin`
- Password: (whatever you set in .env)

## 4. Explore New Features

### Dashboard (/)
- View statistics: total listings, average price, neighborhoods
- See your 10 most recent finds
- Quick navigation

### All Listings (/listings)
- Browse all tracked listings
- Filter by neighborhood
- Filter by price range
- Sortable table

### Run Search (/search)
- Same search form as before
- Now with better error messages
- Validates your input

## 5. Deploy (Optional)

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions for:
- Render (free tier)
- Heroku
- DigitalOcean
- Self-hosted VPS

## What Changed?

### Security ✅
- Password-protected web interface
- Rate limiting to prevent abuse
- Fixed SECRET_KEY vulnerability
- Input validation for searches
- SQL injection protection
- URL validation on redirects

### Features ✅
- Dashboard with statistics
- Filter listings by neighborhood/price
- Better error messages
- Flash notifications
- Clean navigation bar

### Bug Fixes ✅
- Fixed broken test_send.py script
- Better error handling throughout
- Validation prevents crashes

## GitHub Actions

Your existing GitHub Actions workflow continues to work unchanged. It runs independently every 2 hours and uses GitHub Secrets for credentials (which are secure).

## Next Steps

1. **Test locally** - Make sure login works
2. **Run a search** - Test the new validation
3. **Browse listings** - Try the filters
4. **Deploy** - Follow DEPLOYMENT.md if you want remote access

## Troubleshooting

### "No module named 'flask_login'"
```bash
pip install -r requirements.txt
```

### "ADMIN_PASSWORD environment variable must be set"
You need to set ADMIN_PASSWORD in your `.env` file:
```bash
# Add to .env
ADMIN_PASSWORD=your-secure-password
```

### "Invalid username or password"
Check your `.env` file:
```bash
cat .env | grep ADMIN
```

### Can't access the site
Make sure you're running the Flask app:
```bash
python3 -m app.app
```

## Need Help?

- Check [DEPLOYMENT.md](DEPLOYMENT.md) for deployment issues
- Check [CHANGELOG.md](CHANGELOG.md) for detailed changes
- Check [README.md](README.md) for general usage

## Security Reminder

🔒 **Before deploying publicly:**
1. Set a strong ADMIN_PASSWORD
2. Generate a random SECRET_KEY
3. Use HTTPS (SSL/TLS)
4. Keep credentials in .env (never commit to git)
