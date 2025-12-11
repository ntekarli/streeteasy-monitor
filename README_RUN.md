Running StreetEasy Monitor — quick start

1) Create & activate a Python virtual environment

```bash
# Recommended: pyenv + pyenv-virtualenv
pyenv install 3.12.3
pyenv virtualenv 3.12.3 .venv
pyenv local .venv

# Or use venv
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

2) Create a `.env` in the repo root with these variables

```
# Optional previous contact fields
MESSAGE=""
PHONE=""
EMAIL=""
NAME=""

# SMTP (used by EmailNotifier)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-smtp-or-app-password
EMAIL_RECIPIENT=your-email@gmail.com
```

3) Run the CLI scraper

```bash
python main.py
```

4) Run the Flask web UI (port 8002 by default)

```bash
python -m app.app
```

5) (Optional) Run as a cron job

```bash
cd cron
chmod +x *.sh
./create_cron.sh
./start_cron.sh
# to stop:
./stop_cron.sh
```

Notes
- The SQLite DB is created at `data/db.sqlite3` automatically.
- Listings are inserted into the DB only after successful email notification.
- For Gmail, generate an app password if 2FA is enabled.
