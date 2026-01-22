# Fixing 403 Forbidden Errors

## Changes Made to Improve Reliability

### ✅ Implemented (Just Now)

1. **Rotating User Agents** ([config.py](src/streeteasymonitor/config.py))
   - Uses `fake-useragent` library instead of hardcoded Chrome UA
   - Each request gets a different, realistic user agent

2. **Added Referer Header**
   - Requests now appear to come from Google
   - Makes traffic look more organic

3. **Homepage Visit Before Search**
   - Always visits StreetEasy homepage first to establish cookies
   - Mimics real user behavior

4. **Random Initial Delay** ([main.py](main.py))
   - 0-30 second random delay before each run
   - Prevents predictable timing patterns

5. **Removed Suspicious Headers**
   - Removed Chrome-specific fingerprinting headers
   - Kept only standard, essential headers

---

## Testing Steps

### Step 1: Test Locally (Confirms if it's an IP issue)

```bash
# Test locally from your computer
python main.py
```

**If it works locally:**
- ✅ The code changes are working
- ❌ GitHub Actions IPs are blocked by StreetEasy
- → See "Solution for GitHub Actions IP Blocking" below

**If it fails locally:**
- → Continue to Step 2

### Step 2: Check User Agent Library

```bash
# Verify fake-useragent is working
python3 -c "from fake_useragent import UserAgent; ua = UserAgent(); print(ua.random)"
```

Should print a random user agent string. If it errors:
```bash
pip install --upgrade fake-useragent
```

### Step 3: Manual Test Run in GitHub Actions

1. Go to your GitHub repository
2. Click "Actions" tab
3. Click "StreetSweeper - Scheduled Scraper"
4. Click "Run workflow" → "Run workflow" button
5. Check the logs

**Look for:**
- User agent being rotated (different each run)
- "Starting in X seconds" message (random delay)
- Homepage visit before search
- Different error codes or success

---

## Solution for GitHub Actions IP Blocking

If local testing works but GitHub Actions fails with 403, StreetEasy is blocking GitHub's IP ranges. **This is the most common cause.**

### Option A: Switch to Self-Hosted Cron (Recommended)

Use your home computer with a cron job instead of GitHub Actions:

```bash
# Edit crontab
crontab -e

# Add this line (runs every 2 hours)
0 */2 * * * cd /path/to/streeteasy-monitor && /path/to/.venv/bin/python main.py >> cron.log 2>&1
```

**Advantages:**
- Residential IP (less likely to be blocked)
- Free
- More control

**Disadvantages:**
- Computer must stay on
- Need to manage it yourself

### Option B: Use Render/Heroku Cron Jobs

Deploy on Render or Heroku with scheduled jobs instead of GitHub Actions:

**Render (Free Tier):**
1. Deploy the app as a Background Worker
2. Set up Render Cron Jobs
3. Different IP ranges than GitHub

**Heroku:**
1. Use Heroku Scheduler addon
2. Runs on different infrastructure

### Option C: Add Proxy Support (Advanced)

Use a proxy service to route requests through residential IPs:

**1. Add proxy environment variable to GitHub Secrets:**
```
PROXY_URL=http://username:password@proxy-provider.com:8080
```

**2. Update [search.py](src/streeteasymonitor/search.py):**

```python
import os

# In the fetch() method, modify the get request:
proxies = None
if os.environ.get('PROXY_URL'):
    proxies = {
        'http': os.environ.get('PROXY_URL'),
        'https': os.environ.get('PROXY_URL'),
    }

self.r = self.session.get(self.url, timeout=30, proxies=proxies)
```

**Recommended Proxy Services:**
- **ScraperAPI** ($49/mo) - Handles rotation, CAPTCHAs
- **Bright Data** (pay-per-GB) - Residential proxies
- **Webshare** ($2.99/mo) - Budget option
- **SmartProxy** ($12.5/mo) - Rotating residential

**Free Proxy (not recommended):**
- Unreliable
- Often blocked
- Can be malicious
- Free proxy lists change frequently

### Option D: Reduce Frequency

StreetEasy might allow occasional requests but block frequent ones:

**Edit [.github/workflows/scrape.yml](.github/workflows/scrape.yml):**

```yaml
# Instead of every 2 hours, try 3-4 times per day:
on:
  schedule:
    - cron: '15 11 * * *'  # 7:15 AM EST
    - cron: '30 17 * * *'  # 1:30 PM EST
    - cron: '45 21 * * *'  # 5:45 PM EST
    - cron: '20 1 * * *'   # 9:20 PM EST
```

---

## Monitoring and Debugging

### Check What User Agent Was Used

Add this to [search.py](src/streeteasymonitor/search.py) temporarily:

```python
# Right after getting headers
headers = self.session.headers
print(f'{get_datetime()} Using User-Agent: {headers.get("User-Agent")}')
```

### Check if Cookies Are Being Set

```python
# After homepage visit
print(f'{get_datetime()} Cookies: {len(self.session.cookies)} cookies set')
```

### Test Different User Agents

If `fake-useragent` is causing issues, try specific user agents:

```python
# In config.py get_headers():
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]
import random
user_agent = random.choice(user_agents)
```

---

## Long-Term Solutions

### 1. Move Away from Scraping (Best Option)

Check if StreetEasy has an API:
- Less likely to be blocked
- More reliable
- Legal/ToS compliant

### 2. Use a Dedicated Scraping Service

Services like:
- **ScraperAPI** - Handles blocking, rotation, CAPTCHAs
- **Apify** - Pre-built scrapers for many sites
- **ParseHub** - Visual scraper builder

These handle all anti-bot measures for you.

### 3. Accept Email Limitations

Use StreetEasy's built-in email alerts instead:
- Set up saved searches on StreetEasy
- Get email notifications (official feature)
- More reliable than scraping

---

## What to Expect

**Immediate fixes likely to work:**
- ✅ Rotating user agents
- ✅ Homepage visit before search
- ✅ Random delays

**If still getting 403:**
- GitHub Actions IPs are blocked (very likely)
- Need to switch to self-hosted or proxy

**StreetEasy's anti-bot measures:**
- IP-based blocking (most common)
- User agent filtering (now addressed)
- Rate limiting (already handled with delays)
- Behavioral analysis (now addressed with homepage visits)
- CAPTCHA (not encountered yet)

---

## Need Help?

1. **Test locally first** - this tells you if it's an IP issue
2. **Check GitHub Actions logs** - see if user agents are rotating
3. **Try manual trigger** - run workflow manually to test immediately
4. **Consider self-hosted** - most reliable long-term solution

## Summary

**Probable cause:** GitHub Actions IP ranges are blocked by StreetEasy

**Best solutions (in order):**
1. Self-hosted cron job (free, reliable)
2. Render/Heroku scheduled jobs (free tier available)
3. Proxy service ($5-50/mo)
4. Reduce frequency (may work temporarily)

The code improvements will help, but if GitHub's IPs are blocked, you'll need to change hosting platforms.
