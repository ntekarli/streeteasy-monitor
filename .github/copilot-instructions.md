# Copilot-Generated Instructions for StreetSweeper

## Project Overview
StreetSweeper is a rental listing scraper with messaging and web UI components. The project has three major execution paths:
- **CLI**: `python main.py` - scrapes listings and sends messages based on search criteria
- **Flask Web App**: `python -m app.app` - provides UI for manual searches and displays contacted listings
- **Cron Jobs**: `cron/` scripts - manages background execution

## Architecture & Data Flow

### Core Modules (src/streeteasymonitor/)
1. **monitor.py** - Orchestrator that:
   - Sets up `requests.Session` with rotating user agents (via fake-useragent)
   - Initializes Database and Config
   - Coordinates Search → Messager workflow
   - Context manager that closes session on exit

2. **search.py** - URL construction and scraping:
   - Loads `area_map` from `data/areas.json` (StreetEasy neighborhood ID mapping)
   - Builds filter parameters (price, beds, baths, amenities)
   - Fetches HTML via session, passes to Parser (imported but detailed in read_file)
   - Returns list of new listings not in database

3. **database.py** - SQLite persistence:
   - Creates `data/db.sqlite3` automatically
   - Schema: `listings` table with `listing_id` (unique), `created_at`, price, address, neighborhood
   - Key methods: `get_existing_ids()`, `get_listings_sorted()`, `insert_new_listing()`

4. **email_notifier.py** - Email notification system:
   - Sends SMTP email notifications when new listings appear
   - Configurable via `.env` file (SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, EMAIL_RECIPIENT)
   - Formats listing details in email body with address, price, neighborhood, and URL

5. **config.py** - Configuration & environment:
   - `Config.defaults` dict: search parameters (price, beds, neighborhoods, amenities)
   - `Config.filters` dict: exclusion filters (by URL pattern, address, neighborhood)
   - `get_headers()` rotates user agents to avoid blocking
   - `get_email_config()` loads SMTP configuration from environment
   - Reads `.env` via `environs` library

6. **utils.py** - Helpers:
   - `get_area_map()` - loads JSON mapping once (class attribute in Search)
   - `build_url()` - constructs StreetEasy URLs via query params
   - `get_datetime()` - NYC timezone logging

### Flask Application (app/)
- **app.py**: Entry point, runs on port 8002
- **__init__.py**: create_app() factory, defines routes:
  - Integration with Paddaddy API for additional rental info
  - Calls `main()` from main.py for search execution
  - Filters and displays listings from database
- **forms.py**: WTForms SearchForm with SelectMultipleField for neighborhoods
- **templates/**: Bootstrap + HTMX for dynamic updates
- **static/**: CSS, JavaScript (Tom Select for multi-select)

## Critical Patterns

### Session & Header Management
- All requests use a single `requests.Session` initialized in Monitor
- User-Agent rotation via `fake_useragent` prevents blocking
- Session closed via context manager (`with` statement)

### Database Safety
- `insert_new_listing()` uses `INSERT OR IGNORE` to prevent duplicate listing_ids
- All queries use parameterized SQL (prevents injection)
- Timestamps stored in UTC via SQL DEFAULT

### Configuration Override
- Default parameters in `Config.defaults` used by CLI
- `Monitor(**kwargs)` accepts overrides (used by Flask forms)
- Exclusion filters applied post-scrape via Config.filters

## Development Workflows

### Local Testing
```bash
# Run CLI with defaults
python main.py

# Run Flask app (http://localhost:8002)
python -m app.app

# Use .env for API credentials/overrides
```

### Cron Setup (automated, see cron/README if exists)
```bash
chmod +x cron/*.sh
./cron/create_cron.sh  # Creates cron job
./cron/start_cron.sh   # Starts it
./cron/stop_cron.sh    # Stops it
```

### Adding Features
- **New search filters**: Add to Config.defaults and build_url() params
- **New messaging logic**: Extend Messager class (respects StreetEasy API schema)
- **New UI views**: Extend Flask routes in app/__init__.py using SearchForm
- **Database schema changes**: Update Database.create_table() (idempotent)

## Integration Points

### External APIs
- **StreetEasy**: Web scraping for rental listings
- **Paddaddy**: Enriches listings with additional rental data (https://paddaddy.app)
- **SMTP**: Email notifications via configured mail server (Gmail, SendGrid, etc.)
- **fake-useragent**: Rotates user agents to bypass request blocking

### Dependencies
- **Scraping**: requests, beautifulsoup4, fake-useragent
- **Web**: Flask, Flask-WTF, Bootstrap-Flask, HTMX
- **Email**: smtplib (stdlib), email (stdlib)
- **Config**: environs, python-dotenv
- **Database**: sqlite3 (stdlib)

## File Organization Notes
- `src/streeteasymonitor/` is the main package (imports as `from src.streeteasymonitor import ...`)
- `main.py` is CLI entry point, imports from src/ package
- `app/` is Flask package (run via `python -m app.app`)
- `data/` directory created at runtime by Database for SQLite and area mappings
- `cron/` scripts are bash helpers for Linux/Mac cron setup
