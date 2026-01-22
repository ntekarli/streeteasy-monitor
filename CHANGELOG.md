# Changelog

## [2.0.0] - 2026-01-22

### Added - Web Interface & Security Improvements

#### Authentication & Security
- **Flask-Login authentication system** with secure password-protected access
  - Login page with session management
  - Single-user authentication (configurable via environment variables)
  - "Remember me" functionality
  - Secure password hashing with Werkzeug
- **Fixed SECRET_KEY security issue** - now uses environment variable instead of hardcoded 'dev'
- **Rate limiting** on all routes to prevent abuse
  - Login: 10 attempts per minute
  - Search: 5 per minute
  - Global: 200 per day, 50 per hour
- **Input validation** for search parameters
  - Validates area names against available areas
  - Validates price and bedroom ranges
  - Prevents invalid parameter combinations
- **Fixed SQL injection risk** in database.py with column whitelisting
- **Fixed open redirect vulnerability** in URL redirect route
  - Now validates URLs and only allows StreetEasy links

#### Dashboard & UI Improvements
- **New Dashboard page** with statistics:
  - Total listings tracked
  - Average rental price
  - Number of unique neighborhoods
  - Recent listings preview (last 10)
- **Improved Listings page** with filtering:
  - Filter by neighborhood (dropdown)
  - Filter by price range (min/max)
  - Shows result count
  - Better table styling with striped rows
- **Navigation bar** across all authenticated pages:
  - Dashboard link
  - All Listings link
  - Run Search link
  - Logout link
- **Flash messages** for user feedback:
  - Success messages (green)
  - Error messages (red)
  - Info messages (blue)
- **Separated search and view functionality**:
  - `/` - Dashboard (overview)
  - `/listings` - Browse all listings with filters
  - `/search` - Run new searches

#### Database Improvements
- **New database methods**:
  - `get_listings_sorted(limit=None)` - supports limiting results
  - `get_statistics()` - returns aggregated statistics
- **Column whitelisting** for secure inserts
- **Better error handling** for database operations

#### Code Quality & Bug Fixes
- **Fixed broken test script** ([scripts/test_send.py](scripts/test_send.py))
  - Changed `send_listing_notification()` to `send_batch_notification()`
  - Updated to pass list of listings instead of single listing
  - Added missing `listing_id` field
- **Improved error handling** throughout the application
  - Try-catch blocks for search operations
  - Validation errors displayed to user
  - Better exception messages
- **Code validation improvements**:
  - Search parameter validation in [search.py](src/streeteasymonitor/search.py)
  - Price range validation
  - Bedroom count validation
  - Area name validation

#### Documentation
- **Created `.env.example`** - template for environment variables
- **Created DEPLOYMENT.md** - comprehensive deployment guide
  - Instructions for Render, Heroku, DigitalOcean
  - Self-hosting guide with Nginx + systemd
  - Security checklist
  - Troubleshooting section
- **Updated README.md** with:
  - Authentication information
  - New features list
  - Updated configuration section
  - Security notes
  - Updated TODO list

#### Dependencies
- Added **Flask-Login** (0.6.3) for authentication
- Added **Flask-Limiter** (3.5.0) for rate limiting
- Updated **requirements.txt** with new dependencies

### Changed
- **Route structure reorganized**:
  - `/` now shows dashboard instead of search form
  - `/login` for authentication
  - `/logout` for logout
  - `/search` for running searches
  - `/listings` for browsing all listings
- **Form submission** now uses `/search` endpoint
- **Protected all routes** with `@login_required` decorator
- **Improved table layout** in all listings views

### Security Fixes
- SECRET_KEY no longer hardcoded ([app/__init__.py:25](app/__init__.py))
- Admin password now configurable via environment variable
- SQL injection risk mitigated with column whitelisting
- Open redirect vulnerability fixed with URL validation
- Rate limiting prevents brute force attacks

### Deprecated
- Old index route (`/`) now redirects to dashboard

### Technical Details

**Files Modified:**
- `app/__init__.py` - Added authentication, rate limiting, new routes
- `app/templates/layout.html` - Added navigation bar
- `app/templates/form.html` - Updated form action URL
- `src/streeteasymonitor/database.py` - Added validation, new methods
- `src/streeteasymonitor/search.py` - Added input validation
- `scripts/test_send.py` - Fixed method name
- `requirements.txt` - Added Flask-Login, Flask-Limiter
- `README.md` - Updated documentation

**Files Created:**
- `app/templates/login.html` - Login page
- `app/templates/dashboard.html` - Dashboard with statistics
- `app/templates/search.html` - Search form page
- `app/templates/listings.html` - Improved listings browser
- `.env.example` - Environment variable template
- `DEPLOYMENT.md` - Deployment guide
- `CHANGELOG.md` - This file

## Migration Guide

### For Existing Users

1. **Update dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Update your `.env` file** with new required variables:
   ```bash
   SECRET_KEY=<generate with: python -c "import os; print(os.urandom(24).hex())">
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=<your-secure-password>  # REQUIRED - app will not start without this
   ```

   **Important:** `ADMIN_PASSWORD` must be set explicitly. The app will fail to start with a clear error message if it's missing.

3. **Test locally:**
   ```bash
   python -m app.app
   ```
   Navigate to http://localhost:8002 and login with your credentials.

4. **Update deployment** if you have the web interface deployed:
   - Add new environment variables to your hosting platform
   - Redeploy the application

### Breaking Changes

- The root route (`/`) now requires authentication
- Direct access to search form moved to `/search`
- **ADMIN_PASSWORD environment variable is now required** - the app will not start without it (no default password for security reasons)

## Notes

- GitHub Actions workflow continues to work unchanged
- Database schema remains compatible
- Email notifications continue to work as before
- CLI usage (`python main.py`) is unaffected
